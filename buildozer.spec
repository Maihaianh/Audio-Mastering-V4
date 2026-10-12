[app]
title = AM-MHA Pro Mastering
package.name = ammhapro
package.domain = org.ammha

# Các định dạng file nguồn bao gồm
source.include_exts = py,png,jpg,kv,atlas
source.include_dir = 

# Phiên bản ứng dụng
version = 1.0.0

# Các thư viện Python phụ thuộc bắt buộc cho bộ xử lý mastering ngoại tuyến
requirements = python3,kivy,numpy,scipy,plyer

# Cấu hình hướng màn hình và quyền truy cập
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Cấu hình Android API
android.api = 33
android.minapi = 21
