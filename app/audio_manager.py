"""
Audio playback and native Android alarm scheduling abstraction layer.
"""

import threading
import os
import time
from kivy.core.audio import SoundLoader
from kivy.utils import platform

_playing = False
_sound = None
_stop_event = threading.Event()
_volume_stop_event = threading.Event()
_volume_thread = None
_current_sound_path = ""


def get_next_alarm_time_ms(hour: int, minute: int, is_am: bool) -> int:
    from datetime import datetime, timedelta
    import time
    
    now = datetime.now()
    h24 = hour % 12
    if not is_am:
        h24 += 12
        
    alarm_time = now.replace(hour=h24, minute=minute, second=0, microsecond=0)
    if alarm_time <= now:
        alarm_time += timedelta(days=1)
        
    return int(time.mktime(alarm_time.timetuple()) * 1000)


def schedule_android_alarm(hour: int, minute: int, is_am: bool):
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        from android import mActivity
        
        Context = autoclass('android.content.Context')
        AlarmManager = autoclass('android.app.AlarmManager')
        PendingIntent = autoclass('android.app.PendingIntent')
        Intent = autoclass('android.content.Intent')
        
        context = mActivity.getApplicationContext()
        alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
        
        # Target: org.kivy.android.PythonActivity (launch Kivy directly when alarm fires)
        activity_class = autoclass('org.kivy.android.PythonActivity')
        intent = Intent(context, activity_class)
        intent.setAction("org.kangyewon.puzzlealarm.ALARM_TRIGGER")
        intent.putExtra("alarm_trigger", True)
        
        # Bring app to foreground and clear other activities
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
        
        # Request code 1001. FLAG_UPDATE_CURRENT (134217728) | FLAG_IMMUTABLE (67108864) = 201326592
        pending_intent = PendingIntent.getActivity(context, 1001, intent, 201326592)
        
        trigger_time_ms = get_next_alarm_time_ms(hour, minute, is_am)
        
        # Set Alarm Clock info to show alarm icon in status bar and guarantee wake up
        AlarmClockInfo = autoclass('android.app.AlarmManager$AlarmClockInfo')
        show_pending_intent = PendingIntent.getActivity(context, 1002, Intent(context, activity_class), 201326592)
        alarm_clock_info = AlarmClockInfo(trigger_time_ms, show_pending_intent)
        
        alarm_manager.setAlarmClock(alarm_clock_info, pending_intent)
        print(f"Scheduled AlarmManager exact alarm clock wakeup at {trigger_time_ms} ms")
    except Exception as e:
        print(f"Failed to schedule native Android alarm: {e}")


def cancel_android_alarm():
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        from android import mActivity
        
        Context = autoclass('android.content.Context')
        PendingIntent = autoclass('android.app.PendingIntent')
        Intent = autoclass('android.content.Intent')
        
        context = mActivity.getApplicationContext()
        alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
        
        activity_class = autoclass('org.kivy.android.PythonActivity')
        intent = Intent(context, activity_class)
        intent.setAction("org.kangyewon.puzzlealarm.ALARM_TRIGGER")
        
        pending_intent = PendingIntent.getActivity(context, 1001, intent, 201326592)
        alarm_manager.cancel(pending_intent)
        print("Cancelled AlarmManager alarm successfully.")
    except Exception as e:
        print(f"Failed to cancel native Android alarm: {e}")


def _volume_enforcer_loop(stop_event: threading.Event) -> None:
    try:
        from jnius import autoclass
        from android import mActivity
        
        Context = autoclass('android.content.Context')
        AudioManager = autoclass('android.media.AudioManager')
        
        context = mActivity.getApplicationContext()
        audio_manager = context.getSystemService(Context.AUDIO_SERVICE)
        
        while not stop_event.is_set():
            try:
                # Force maximum alarm volume on STREAM_ALARM channel
                max_vol = audio_manager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
                audio_manager.setStreamVolume(AudioManager.STREAM_ALARM, max_vol, 0)
            except Exception:
                pass
            time.sleep(0.5)
    except Exception as e:
        print(f"Volume enforcer thread setup failed: {e}")


def _show_fullscreen_notification_android():
    try:
        from jnius import autoclass
        from android import mActivity
        
        Context = autoclass('android.content.Context')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        
        context = mActivity.getApplicationContext()
        channel_id = "alarm_channel"
        channel_name = "Alarm Notification Channel"
        importance = 4  # NotificationManager.IMPORTANCE_HIGH
        
        notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)
        
        Build = autoclass('android.os.Build$VERSION')
        if Build.SDK_INT >= 26:
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.enableVibration(True)
            channel.setBypassDnd(True)
            notification_manager.createNotificationChannel(channel)
            
            NotificationBuilder = autoclass('android.app.Notification$Builder')
            builder = NotificationBuilder(context, channel_id)
        else:
            NotificationBuilder = autoclass('android.app.Notification$Builder')
            builder = NotificationBuilder(context)
            
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        intent = Intent(context, PythonActivity)
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
        
        pending_intent = PendingIntent.getActivity(context, 0, intent, 201326592)
        
        builder.setSmallIcon(17301555)  # android.R.drawable.ic_lock_idle_alarm
        builder.setContentTitle("Puzzle Alarm")
        builder.setContentText("Alarm is ringing! Tap to solve puzzles.")
        builder.setPriority(2)  # Notification.PRIORITY_MAX
        builder.setCategory("alarm")
        builder.setFullScreenIntent(pending_intent, True)
        
        notification_manager.notify(999, builder.build())
        print("Heads-up / FSI notification displayed.")
    except Exception as e:
        print(f"Failed to display full-screen intent notification: {e}")


def play_alarm(sound_path: str = "") -> None:
    global _playing, _sound, _volume_thread, _volume_stop_event, _current_sound_path
    if _playing:
        return
    _playing = True
    _current_sound_path = sound_path

    # On Android, launch volume enforcer and FSI notification
    if platform == 'android':
        _volume_stop_event.clear()
        _volume_thread = threading.Thread(target=_volume_enforcer_loop, args=(_volume_stop_event,), daemon=True)
        _volume_thread.start()
        _show_fullscreen_notification_android()

    # Load sound file (use default_alarm.wav in root if path is empty/invalid)
    if not sound_path or not os.path.isfile(sound_path):
        sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "default_alarm.wav")

    if sound_path and os.path.isfile(sound_path):
        try:
            _sound = SoundLoader.load(sound_path)
            if _sound:
                _sound.loop = True
                _sound.play()
                return
        except Exception as e:
            print(f"Error loading Kivy sound: {e}")


def pause_alarm() -> None:
    global _playing, _sound, _volume_stop_event
    if not _playing:
        return
    
    if platform == 'android':
        _volume_stop_event.set()
        
    if _sound:
        try:
            _sound.stop()
        except Exception:
            pass
    _playing = False


def resume_alarm() -> None:
    global _playing, _sound, _current_sound_path
    if not _playing:
        play_alarm(_current_sound_path)
        return

    if _sound:
        try:
            _sound.play()
        except Exception:
            pass


def stop_alarm() -> None:
    global _playing, _sound, _volume_stop_event
    _playing = False
    
    if platform == 'android':
        _volume_stop_event.set()
        try:
            from jnius import autoclass
            from android import mActivity
            NotificationManager = autoclass('android.app.NotificationManager')
            notification_manager = mActivity.getApplicationContext().getSystemService(mActivity.getApplicationContext().NOTIFICATION_SERVICE)
            notification_manager.cancel(999)
        except Exception:
            pass

    if _sound:
        try:
            _sound.stop()
            _sound.unload()
        except Exception:
            pass
        _sound = None
