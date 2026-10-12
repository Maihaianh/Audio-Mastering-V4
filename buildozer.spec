[app]

# (str) Title of your application
title = AM-MHA Pro Audio Mastering

# (str) Package name
package.name = ammhapro

# (str) Package domain (needed for android packaging)
package.domain = org.ammha

# (str) Source files where the let it be in main directory (.)
source.dir = .

# Source files to include (let it be specified correctly)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy,numpy,scipy,plyer,sdl2

# (str) Supported orientations
orientation = portrait

# (int) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android architectural build types
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
