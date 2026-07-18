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


def main():
    print("Background Alarm Service started.")
    
    # Track the last fired minute to avoid double triggers within the same minute
    fired_minute = None # (hour24, minute, day)
    
    # Active media player instance
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
        # Fallback or exit if not on Android
        return

    # Check loop
    while True:
        try:
            # Check if alarm needs to ring
            settings = load_settings()
            if settings and settings.get("enabled", True):
                hour = settings.get("hour", 7)
                minute = settings.get("minute", 0)
                is_am = settings.get("is_am", True)
                
                h24 = hour % 12
                if not is_am:
                    h24 += 12
                
                now = datetime.now()
                
                # Trigger condition
                if (
                    now.hour == h24
                    and now.minute == minute
                    and fired_minute != (h24, minute, now.day)
                ):
                    fired_minute = (h24, minute, now.day)
                    print(f"Alarm triggered at {h24:02d}:{minute:02d}")
                    
                    # Create the ringing flag file
                    files_dir = context.getFilesDir().getAbsolutePath()
                    flag_file = os.path.join(files_dir, "app", ".ringing")
                    os.makedirs(os.path.dirname(flag_file), exist_ok=True)
                    with open(flag_file, "w") as f:
                        f.write("ringing")
                    
                    # Launch the Kivy app
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
                        if player:
                            try:
                                player.stop()
                                player.release()
                            except Exception:
                                pass
                            player = None
                        
                        player = MediaPlayer()
                        sound_path = settings.get("sound_path", "")
                        if sound_path and os.path.isfile(sound_path):
                            player.setDataSource(sound_path)
                        else:
                            uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                            if not uri:
                                uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
                            player.setDataSource(context, uri)
                        
                        player.setAudioStreamType(AudioManager.STREAM_ALARM)
                        player.prepare()
                        player.setLooping(True)
                        player.start()
                    except Exception as ex:
                        print(f"Failed to prepare or start media player: {ex}")
            
            # If alarm is currently ringing, enforce max volume and check if flag is deleted
            files_dir = context.getFilesDir().getAbsolutePath()
            flag_file = os.path.join(files_dir, "app", ".ringing")
            if os.path.exists(flag_file):
                if player and player.isPlaying():
                    # Enforce maximum alarm volume (user requirement #4)
                    try:
                        max_vol = audio_manager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
                        audio_manager.setStreamVolume(AudioManager.STREAM_ALARM, max_vol, 0)
                    except Exception as ex:
                        print(f"Failed to enforce max volume: {ex}")
            else:
                # If flag is deleted (user solved the puzzle), stop the player
                if player:
                    try:
                        player.stop()
                        player.release()
                    except Exception as ex:
                        print(f"Failed to stop player: {ex}")
                    player = None
                    print("Alarm stopped by user.")
                    
        except Exception as e:
            print(f"Error in service loop: {e}")
            
        time.sleep(1.0) # Check every second

if __name__ == '__main__':
    main()
