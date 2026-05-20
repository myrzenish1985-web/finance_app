[app]

title = МоиФинансы
package.name = financeapp
package.domain = org.myfinance

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy

orientation = portrait

fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25c
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
