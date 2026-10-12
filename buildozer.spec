[app]

# (str) Title of your application
title = AM-MHA Pro Audio Mastering

# (str) Package name
package.name = ammhapro

# (str) Package domain (needed for android packaging)
package.domain = org.ammha

# (str) Version of the application
version = 1.0

# (str) Source files where the let it be in main directory (.)
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy,plyer,sdl2

# (str) Supported orientations
orientation = portrait

# (int) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android architectural build types (build riêng cho arm64-v8a để tối ưu numpy/scipy)
android.archs = arm64-v8a

# (str) Cố định phiên bản NDK ổn định tương thích tốt với numpy và scipy
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
