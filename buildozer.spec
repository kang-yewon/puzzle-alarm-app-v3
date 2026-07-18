[app]

# (str) Title of your application
title = Puzzle Alarm

# (str) Package name
package.name = puzzlealarm

# (str) Package domain (needed for android packaging)
package.domain = org.kangyewon

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,wav,ttf,json

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*placeholder*

# (list) List of directory to exclude
#source.exclude_dirs = tests, bin, venv

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1

# (str) Custom source folders for requirements
# It may be useful when requirements are not in pypi
#requirements.source.kivy = ../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
services = alarm:service.py


#
# Android specific
#

# (bool) Indicate if the XML export should be support (for android 10+)
#android.enable_androidx = True

# (list) Permissions
android.permissions = WAKE_LOCK, VIBRATE, RECEIVE_BOOT_COMPLETED, DISABLE_KEYGUARD, SYSTEM_ALERT_WINDOW, USE_FULL_SCREEN_INTENT, POST_NOTIFICATIONS

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Accept SDK license without prompting
android.accept_sdk_license = True

# (str) Android NDK version to use
#android.ndk = 25b

# (str) Android SDK directory to use
#android.sdk_path =

# (str) Android NDK directory to use
#android.ndk_path =

# (bool) Use --private data directory (True, default) or --dir public directory (False)
#android.private_storage = True

# (str) Android entry point, default is PythonActivity
#android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to exclude for shrink resources
#android.shrink_resources_exclude = 

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) Packaging options to pass to Gradle
#android.packaging_options =

# (list) Java files to add to the project (list of absolute or relative paths)
#android.add_src =

# (list) Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In newer buildozer versions, you can specify multiple archs separated by comma.
android.archs = arm64-v8a, armeabi-v7a

# (bool) Fullscreen mode, execution will still have bands if set to false
fullscreen = 1

# (str) Extra xml dumps
#android.extra_manifest_xml =

# (list) Android additionnal resource dirs
#android.add_resources =

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, default is master
#p4a.branch = master


#
# Buildozer section
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1

# (str) Path to build artifact storage, default is info directory
bin_dir = ./bin
