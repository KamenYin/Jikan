![banner](screenshots/banner_wide2.png)


# JIKAN・ジカン
   - derived from the Japanese word for time *時間*


## Preview

![Preview](visuals/General_Flow_en.gif)

***
<br>



## Built With

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySide6](https://img.shields.io/badge/PySide6-Qt-green)



- Qt Linguist*
- Typescript*
   * *Used for translations

- GUI:
  - PySide6 (Qt for Python)

- Time/Date Management:
  - QDateTime
  - QTimeZone
  

- Time Handling:
  - QTimer 
 


- Language Support 【EN/JP】:
  - Qt Linguist
  - QLocale

- Styling:
  - Qt Style Sheets (QSS)
     

- Media Playback :
  - QtMultimedia (QMediaPlayer, QAudioOutput)
  - File Handling (pathlib, shutil)
  - Audio Sources:
    - [Miyanova](https://miyanova.com)
    - [EpidemicSound](https://www.epidemicsound.com)

***
<br>

## Installion

**Prerequisites**
- Python 3.10 or higher


***

**Clone the Repository**
- `git clone https://github.com/yourusername/jikan.git`
- `cd Jikan`


**Create a Virtual Environment**

Windows
  - `python -m venv .venv`
  - `\.venv\Scripts\activate`

MacOS/Linux
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`


**Install Dependencies**
- `pip install -r requirements.txt `

**Run the Application**
- `py app.py`
  







## Features

- Clock / Timer / Stopwatch / Pomodoro Clock / Alarm Clock
- Localized Formatting (Date & Time)
- English & Japanese Supported
- Light/Dark Mode
- Timezone based (Clock & Alarm)
- Custom Ringtones (Alarm)


***

## About

This project is intended to serve as a support resource for various daily activities which involve time management. It features five (5) main components namely **Time/Date Display**, **Timer**, **Stopwatch**, **Pomodoro** **Timer** & **Alarm**. Each can be accessed in turn by pressing the button at the upper left hand corner of the window, whereas the button at the upper right manages the light and dark mode toggle. Presently the app supports both English and Japanese. Support may be extended to other languages in future.

***

<br>

 _**The time & date format is rendered based on the user's respective system settings.**_
 

#### English Version

![Eng1](screenshots/time_date_format_eng.png)

***

![Eng2](screenshots/lang_en.png)

***

<br>



#### Japanese Version

![JP1](<screenshots/image-2.png>)

***

![JP2](<screenshots/image-3.png>)

***

<br>


## How To Use

The app comprises of five (5) main features which function independent of each other. This allows for seamless simultaneous use. Each feature is explained in turn below.



### Time/Date Display 

- Displays the current time and date based on the corresponding settings of the user's system. This means that it's possible to have overlapping formats. For example, Display Language being set to Japanese, however the calendar format being the Gregorian Calendar.



EN/EN 
![EN ONLY](<screenshots\eng_date.png>)

***

<br>

JP/EN
![JP & EN](<screenshots/image-6.png>)　

***

<br>



### Timer

- Once the timer has expired an alert will fire to signal the timer's end. Here the user can dismiss the alert by clicking (anywhere) within the window.

- The time range to be counted is set by either typing or using the **+** & **-** buttons respectively (1 minute increments).

- The time can be paused and/or reset using the respective buttons.


<br>
<br>

![Timer Demo](visuals\Timer_Flow_en.gif)

***

<br>

### Stopwatch

- Extends the standard functions of a stopwatch i.e. measuring / recording elapsed time.

- Laps are also accounted for, the maximum number currently supported being seven (7). 

<br>

![Stopwatch Demo](visuals\Stopwatch_en.gif)

***


### Pomodoro

- Based on the Pomodoro Technique i.e. four (4) sessions of  twenty-five (25) minutes with a five (5) minute break in between each session. After the fourth session, a longer break of fifteen (15) minutes is awarded.

- In this rendition the standard pomodoro is the default, however, the respective sessions can be customized freely.
The range for each interval being 1 - 60 



<br>

![Pomodoro Demo](visuals/Pomodoro_en.gif)

***
<br>


### Alarm

- Provides standard alarm features which take into account the
current date and time and by extension the timezone which is determined based on the user's system settings. The time and date set can't be in the past. On startup this is handled by blocking the input using a validator, afterwards the time set will be handled as the following day.


![Alarm Demo 1](visuals\Alarm1_en.gif)

***

<br>


- Allows snoozing where both the snooze duration and the number intervals can be customized. 



![Alarm Demo 2](visuals\Alarm2_en.gif)
***

<br>

- A custom alarm name can be set if desired as well as the alarm frequency i.e. every day or a specific day of the week

- The ringtone can also be customized whether by choosing from the tones provided or by uploading your own. Supported formats include __.mp3, .wav, .ogg, .flac, .m4a, .


![Alarm Demo 3](visuals\Alarm3_en.gif)
***
<br>

- In the event where the window isn't active, a popup will be rendered where the name (if one was set) & time of the alarm will be displayed. Here the user can either stop the alarm or snooze (if enabled).



![Alarm Demo 4](visuals\Alarm4_en.gif)
***

<br>



## Credits

- [PythonGUIs PySide6 Tutorial by Martin Fitzpatrick](https://www.pythonguis.com/pyside6-tutorial)

- [Google Fonts](https://fonts.google.com/)
    - Source used for icons and fonts

- [Animated Toggle Button - Python, PySide6, Qt Widgets - MODERN GUI - Custom Widget by Wanderson](https://youtube.com/watch?v=NnJFi285s3M&si=K-zrwg7MN7MYOswP)

- [Miyanova](https://miyanova.com)

- [EpidemicSound](https://www.epidemicsound.com)
    




## Contact
- GitHub: [KamenYin](https://github.com/KamenYin) 
- Email:  theofficialkamen@gmail.com


























