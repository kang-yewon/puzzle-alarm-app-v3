import os
import time
from datetime import datetime
import json

def get_settings_file_path() -> str:
    try:
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        if service:
            context = service.getApplicationContext()
            files_dir = context.getFilesDir().getAbsolutePath()
            return os.path.join(files_dir, "app", ".puzzle_alarm_settings.json")
    except Exception:
         pass
    return os.path.join(os.path.expanduser("~"), ".puzzle_alarm_settings.json")


def load_settings():
    path = get_settings_file_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def show_fullscreen_notification(context):
    try:
        from jnius import autoclass
        
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        
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
            
        # Intent to launch Kivy App main activity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        intent = Intent(context, PythonActivity)
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK)
        
        # Pending Intent flags: FLAG_UPDATE_CURRENT (134217728) | FLAG_IMMUTABLE (67108864) = 201326592
        pending_intent = PendingIntent.getActivity(context, 0, intent, 201326592)
        
        # Set small icon (standard android alarm icon: android.R.drawable.ic_lock_idle_alarm = 17301555)
        builder.setSmallIcon(17301555)
        builder.setContentTitle("Puzzle Alarm")
        builder.setContentText("Alarm is ringing! Tap to solve puzzles.")
        builder.setPriority(2)  # Notification.PRIORITY_MAX = 2
        builder.setCategory("alarm")
        builder.setFullScreenIntent(pending_intent, True)
        
        notification = builder.build()
        
        # Show FSI notification
        notification_manager.notify(999, notification)
        print("Fullscreen notification triggered successfully.")
    except Exception as e:
        print(f"Failed to build/trigger fullscreen notification: {e}")


def main():
    print("Background Alarm Service started.")
    
    player = None
    
    try:
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        context = service.getApplicationContext()
        MediaPlayer = autoclass('android.media.MediaPlayer')
        AudioManager = autoclass('android.media.AudioManager')
        RingtoneManager = autoclass('android.media.RingtoneManager')
        audio_manager = context.getSystemService(context.AUDIO_SERVICE)
    except Exception as e:
        print(f"Failed to load Android JNI classes in service: {e}")
        return

    # Check if alarm is enabled
    settings = load_settings()
    if not settings or not settings.get("enabled", True):
        print("Alarm is disabled, exiting service immediately.")
        return

    # Create the ringing flag file
    files_dir = context.getFilesDir().getAbsolutePath()
    flag_file = os.path.join(files_dir, "app", ".ringing")
    os.makedirs(os.path.dirname(flag_file), exist_ok=True)
    with open(flag_file, "w") as f:
        f.write("ringing")

    # Trigger FullScreen Intent notification (wakes up screen on Android)
    show_fullscreen_notification(context)

    # Launch Kivy app main activity
    try:
        Intent = autoclass('android.content.Intent')
        package_manager = context.getPackageManager()
        launch_intent = package_manager.getLaunchIntentForPackage("org.kangyewon.puzzlealarm")
        if launch_intent:
            launch_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(launch_intent)
    except Exception as ex:
        print(f"Failed to launch Kivy App: {ex}")

    # Start audio playback
    try:
        player = MediaPlayer()
        
        # Load custom sound if specified and exists, otherwise default to local default_alarm.wav asset
        sound_path = settings.get("sound_path", "")
        if not sound_path or not os.path.isfile(sound_path):
            sound_path = os.path.join(files_dir, "app", "default_alarm.wav")
            
        if os.path.isfile(sound_path):
            player.setDataSource(sound_path)
        else:
            # Final fallback to standard alarm uri
            uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            if not uri:
                uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
            player.setDataSource(context, uri)
        
        player.setAudioStreamType(AudioManager.STREAM_ALARM)
        player.prepare()
        player.setLooping(True)
        player.start()
        print("Media player started playing sound.")
    except Exception as ex:
        print(f"Failed to prepare or start media player: {ex}")

    # Ringing loop: enforce max volume and check if flag is deleted
    while True:
        try:
            if not os.path.exists(flag_file):
                print("Ringing flag deleted. Stopping alarm.")
                break
                
            if player and player.isPlaying():
                # Enforce maximum alarm volume (user requirement #4)
                try:
                    max_vol = audio_manager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
                    audio_manager.setStreamVolume(AudioManager.STREAM_ALARM, max_vol, 0)
                except Exception as ex:
                    print(f"Failed to enforce max volume: {ex}")
        except Exception as e:
            print(f"Error in service loop: {e}")
            
        time.sleep(1.0) # Check every second

    # Cleanup
    if player:
        try:
            player.stop()
            player.release()
        except Exception as ex:
            print(f"Failed to release player: {ex}")
        player = None
    print("Service completed and exiting.")

if __name__ == '__main__':
    main()
