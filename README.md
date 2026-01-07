# GreenBoost

## Русский
GreenBoost — небольшая утилита для Windows, которая показывает состояние системы и помогает быстро очищать временные файлы. Приложение живет в трее, умеет запускаться с Windows и может выполнять автоочистку по заданным условиям.

<img alt="Banner" src="https://i.ibb.co/PZwwGzm5/image.png">
Скачать: https://github.com/lordofsunshine/greenboost/releases/download/v.0.0.1/GreenBoost.exe

**Что умеет:**
- Индекс нагрузки (RAM, pagefile, диск C:, размер temp)
- Быстрая, глубокая и кастомная очистка
- Автоочистка по таймеру и условиям (нагрузка, temp, простой)
- Автозапуск (через реестр или Планировщик заданий)
- Логи и уведомления

**Требования:**
- Windows 10/11
- Python 3.x

**Запуск:**
```
python -m pip install -r requirements.txt
python main.py
```
Запуск в трей:
```
python main.py --tray
```
Проверка метрик (smoke):
```
python main.py --smoke
```

**Сборка:**
```
build\build.ps1
```

**Где лежат настройки и логи:**
- Настройки: `%APPDATA%\GreenBoost\config.json`
- Логи: `%APPDATA%\GreenBoost\logs\greenboost.log`

**Примечания:**
- Некоторые действия требуют прав администратора (например, очистка DNS и изменение параметра pagefile).
- Если приложение не открывается, оно может быть свернуто в трей.

## English
GreenBoost is a small Windows utility that shows system health and helps you clean temporary files quickly. It lives in the tray, can start with Windows, and supports automatic cleanup based on conditions.

<img alt="Banner" src="https://i.ibb.co/PZwwGzm5/image.png">
Download: https://github.com/lordofsunshine/greenboost/releases/download/v.0.0.1/GreenBoost.exe

**Key features:**
- System load index (RAM, pagefile, C: disk, temp size)
- Quick, deep, and custom cleanup
- Auto-clean on a timer with conditions (load, temp size, idle time)
- Autostart (registry or Task Scheduler)
- Logs and notifications

**Requirements:**
- Windows 10/11
- Python 3.x

**Run:**
```
python -m pip install -r requirements.txt
python main.py
```
Start in tray:
```
python main.py --tray
```
Metrics smoke test:
```
python main.py --smoke
```

**Build:**
```
build\build.ps1
```

**Config and logs:**
- Config: `%APPDATA%\GreenBoost\config.json`
- Logs: `%APPDATA%\GreenBoost\logs\greenboost.log`

**Notes:**
- Some actions require administrator privileges (e.g., DNS flush and pagefile setting).
- If the app does not open, it may be minimized to the system tray.
