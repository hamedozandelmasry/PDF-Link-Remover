[app]
title = PDF Link Remover
package.name = pdflinkremover
package.domain = org.copilot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy,pypdf,android

permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
