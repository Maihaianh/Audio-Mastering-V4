[app]
title = AM-MHA Pro Audio Mastering
package.name = ammhapro
package.domain = org.ammha
version = 1.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

requirements = python3,kivy,plyer,sdl2

orientation = portrait
fullscreen = 0

# Bổ sung đầy đủ quyền đọc/ghi bộ nhớ cho Android hiện đại
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, INTERNET

android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
