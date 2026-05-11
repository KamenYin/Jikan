from PySide6.QtCore import Qt,Property,QMimeDatabase, QEvent, QUrl, QPropertyAnimation, QEasingCurve, QRect ,QDateTime, QSize, QTimeZone, QTime, QTimer, Signal, QLocale, QTranslator
from PySide6.QtGui import QIcon, QPixmap,QPainter,QTextCharFormat, QColor, QBrush, QFont
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QApplication,
    QTimeEdit,
    QDateEdit,
    QCalendarWidget,
    QToolButton,
    QCheckBox,
    QSpinBox,
    QSizePolicy,
    QFileDialog
   
    

)

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from pathlib import Path
import re
import sys
import shutil




"""
明日の予定
目覚まし時計を終わらせたり
着信音を加えたり
アラームの設定メニューを作ったりするつもりです。

じゃあ、これ以上…またねー


"""


class Alarm(QWidget):
    alarm_signal = Signal(bool)
    snooze_signal = Signal(bool)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("アラーム")
        #self.setFixedSize(300,300)
        self.alarm_icon = QIcon(QPixmap("taima_icons/alarm_icon.png"))
        self.snooze_icon = QIcon(QPixmap("taima_icons/snooze_icon.png"))
        self.alarm_on_icon = QIcon(QPixmap("taima_icons/alarm_on_icon.png"))
        self.alarm_off_icon = QIcon(QPixmap("taima_icons/alarm_off_icon.png"))
        self.settings_icon = QIcon(QPixmap("taima_icons/settings_icon.png"))
        self.alarm_pause_icon = QIcon(QPixmap("taima_icons/alarm_pause_icon.png"))
        self.check_icon = QIcon(QPixmap("taima_icons/check_icon.png"))
        self.is_enabled = True
        self.user_timezone_id = QTimeZone.systemTimeZoneId()
        self.target_tz = QTimeZone(self.user_timezone_id)
        self.snz_ct_str = ""
        
       

      

    
        self.alarm_timer = QTimer()
        self.alarm_timer.setTimerType(Qt.PreciseTimer)
        self.alarm_timer.timeout.connect(self.trigger_alarm)
        self.alarm_timer.setInterval(1000) #OSによってQTimerの精度が決まるんのでずれを防ぐため1000より900設定したほうがいいと気づいた
        

        self.notif_timer = QTimer()
        self.notif_timer.setSingleShot(True)


        self.snooze_timer = QTimer()
        self.snooze_timer.timeout.connect(self.render_snooze_timer)
        self.snooze_timer.setInterval(1000)

        





        self.alarm_menu = None
        self.alarm_popup = None #目覚まし時計セクションは待機してる場合表示される
        self.snooze_popup = None


        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.preview_allowed = True
        self.alarm_cleared = False

        self.audio_player.setAudioOutput(self.audio_output)

        
       

        # Opted to use a custom Calendar for UX purposes
        self.calendar_ = QCalendarWidget()
        self.calendar_.setGridVisible(False)
        self.calendar_.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.wkend_format = QTextCharFormat()
        self.wkend_format.setForeground(QBrush(QColor("#A600FF")))
        self.calendar_.setWeekdayTextFormat(Qt.Sunday, self.wkend_format) 
        self.calendar_.setWeekdayTextFormat(Qt.Saturday, self.wkend_format) 
        

        self.prev_btn = self.calendar_.findChild(QToolButton, "qt_calendar_prevmonth")
        self.next_btn = self.calendar_.findChild(QToolButton, "qt_calendar_nextmonth")
        self.nav_bar = self.calendar_.findChild(QWidget, "qt_calendar_navigationbar")
        self.top_format = QFont()
        self.top_format.setBold(True)
        self.top_format.setPointSize(15.0)
        self.nav_bar.setFont(self.top_format)


        

        self.prev_btn.setArrowType(Qt.NoArrow)
        self.next_btn.setArrowType(Qt.NoArrow)

        self.today_format = QTextCharFormat()
        self.today_format.setBackground(QColor("#8412EF"))
        self.today_format.setForeground(QColor("#e8d7f7"))
        self.today_format.setFontWeight(QFont.Bold)


        self.header_format = QTextCharFormat()
        self.header_format.setFontWeight(QFont.Weight.Bold)
        self.header_format.setFontPointSize(12.5)
        self.calendar_.setHeaderTextFormat(self.header_format)

        if self.prev_btn and self.next_btn:
            # It's pretty weird but apparently Pyside as the names of the buttons backwards as such I flipped the images
            # i.e. prev == right next == left when it should be the opposite
            self.prev_btn.setIcon(QIcon(QPixmap("taima_icons/right_icon.png")))
            self.next_btn.setIcon(QIcon(QPixmap("taima_icons/left_icon.png")))


          

            self.prev_btn.setIconSize(QSize(40,30))
            self.next_btn.setIconSize(QSize(40,30))

            self.prev_btn.setFixedHeight(50)
            self.next_btn.setFixedHeight(50)


        # Instead of using a single QDT edit for UX purposes I'll use QDateEdit & QTimeEdit instead
        # and then pass them to QDateTime()
        #self.datetime_edit = QDateTimeEdit()
        self.dt_ = QDateTime.currentDateTime(self.target_tz)
        self.user_dt = None
        self.date_edit_ = QDateEdit()
        self.time_edit_ = QTimeEdit()
        

        


       
 
        self.date_edit_.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_edit_.setAlignment(Qt.AlignmentFlag.AlignLeft)

        


        

       
                                
        self.notif_ = QLabel("")
        self.notif_.setObjectName('alarm_notif')
        self.notif_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        


        self.date_edit_.setLocale(QLocale.system())
        #self.date_edit_.setDisplayFormat(QLocale.system().dateFormat(QLocale.FormatType.ShortFormat))
        self.date_edit_.setMinimumDate(self.dt_.date())
        self.calendar_.setDateTextFormat(self.dt_.date(), self.today_format)
        self.date_edit_.setCalendarPopup(True)
        self.date_edit_.setCalendarWidget(self.calendar_)

        

        #バグの由来
        #最初からsetDisplayFormat("HH:mm")を設定したからtime_edit_の最低時間はHH:mm:00っと思っちゃった。でも、実際にははっきり設定しないとダメだからこそ以下のコードを追加する
        self.time_edit_.setDisplayFormat("HH:mm")
        self.time_edit_.setMinimumTime(QTime(self.dt_.time().hour(), self.dt_.time().minute(), 0, 0))
        self.time_edit_.setSelectedSection(QTimeEdit.MinuteSection)


        self.next_alarm_string = ''
        self.is_snoozing = False
        
        self.datetime_ = QDateTime()
        
        self.snooze_btn = QPushButton()
        self.snooze_btn.setFixedSize(QSize(100,100))

        self.dt_submit = QPushButton()
        self.dt_submit.setIcon(self.check_icon)
        self.dt_submit.setFixedSize(QSize(80,40))
        self.dt_submit.setObjectName('dt_submit')
       

        self.dt_submit.setVisible(False)

        self.silence_btn = QPushButton()
        self.silence_btn.setFixedSize(QSize(100,100))


        self.snooze_btn.setObjectName("alarm_outer_btn")
        self.silence_btn.setObjectName("alarm_outer_btn")
       
        # 以下のは真ん中に置こう
        self.alarm_on_off_btn = QPushButton() # activates/deactivates the alarm
        self.alarm_settings_btn = QPushButton() # responsible for calling the settings menu which will enable the user to customize the alarm to their liking
        self.alarm_on_off_btn.setFixedSize(QSize(110,60))
        self.alarm_settings_btn.setFixedSize(QSize(110,60))

        self.alarm_on_off_btn.setObjectName("alarm_inner_btn")
        self.alarm_settings_btn.setObjectName("alarm_inner_btn")

        


        self.snooze_btn.setIcon(self.snooze_icon)
        self.silence_btn.setIcon(self.alarm_pause_icon)
        self.alarm_on_off_btn.setIcon(self.alarm_off_icon)
        self.alarm_settings_btn.setIcon(self.settings_icon)



        
        self.main_layout = QVBoxLayout(self) 

        self.datetime_box = QFrame()
        self.datetime_box.setFrameShape(QFrame.Shape.NoFrame)

        self.datetime_layout = QHBoxLayout()
        self.datetime_layout.addWidget(self.date_edit_, alignment=Qt.AlignmentFlag.AlignLeft)
        self.datetime_layout.addStretch(1)
        self.datetime_layout.addWidget(self.dt_submit, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.datetime_layout.addStretch(1)
        self.datetime_layout.addWidget(self.time_edit_, alignment=Qt.AlignmentFlag.AlignRight)
        self.datetime_box.setLayout(self.datetime_layout)



        self.con_panel = QFrame()
        self.con_layout = QGridLayout() # responsible for holding the alarm controls


        self.mid_frame = QFrame()
        self.mid_layout = QHBoxLayout() # responsible for holding the middle buttons 
        self.con_panel.setFixedHeight(120)
      

        self.mid_layout.addWidget(self.alarm_on_off_btn)
        self.mid_layout.addWidget(self.alarm_settings_btn)
        self.mid_frame.setLayout(self.mid_layout)


        


        self.con_layout.addWidget(self.silence_btn, 0,0)
        self.con_layout.addWidget(self.mid_frame, 0,1)
        self.con_layout.addWidget(self.snooze_btn, 0,2)

        self.notif_.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.con_panel.setLayout(self.con_layout)
        self.notif_box = QFrame()
        self.notif_box.setFixedHeight(40)
        self.notif_layout = QHBoxLayout()
        self.notif_layout.addWidget(self.notif_)
        self.notif_box.setLayout(self.notif_layout)

        self.main_layout.addWidget(self.notif_box, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.datetime_box)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.con_panel)


        self.alarm_name = ''
        self.frequency_ = ''
        self.has_snoozing = False
        self.snz_intervals = 0
        self.snz_duration = 0
        self.is_ringing = False
        
        

        
        #ボタンを繋ぐ
        self.alarm_on_off_btn.clicked.connect(self.set_enabled)
        self.alarm_settings_btn.clicked.connect(self.open_settings_menu)
        self.date_edit_.userDateChanged.connect(self.render_submit)
        self.time_edit_.userTimeChanged.connect(self.render_submit)
        self.date_edit_.userDateChanged.connect(self.set_min_time)
        self.time_edit_.userTimeChanged.connect(self.set_min_time)
        self.snooze_btn.clicked.connect(self.handle_snooze)
        self.snooze_btn.clicked.connect(self.snooze_checker)
        self.silence_btn.clicked.connect(self.stop_alarm)
        self.dt_submit.clicked.connect(self.set_alarm)
        
        self.notif_.setVisible(False)
       
        self.setLayout(self.main_layout)


    def set_min_time(self):
        if self.date_edit_.date() == self.dt_.date():
            self.time_edit_.setMinimumTime(QTime(self.dt_.time().hour(), self.dt_.time().minute(), 0, 0))
        else:
            self.time_edit_.setMinimumTime(QTime(0,0,0,0))


    def render_submit(self):
        if not self.is_ringing:
            self.dt_submit.setVisible(True)

    def set_alarm(self):
       if self.is_enabled:
            self.alarm_timer.start()
            self.user_dt = QDateTime(
                        self.date_edit_.date(),
                        self.time_edit_.time(),
                        self.target_tz
                    )
            now = QDateTime.currentDateTime(self.target_tz)

            if self.user_dt <= now:
                    self.user_dt = self.user_dt.addDays(1)
                    self.date_edit_.setDate(self.user_dt.date())


            if (now.daysTo(self.user_dt) == 0) or (now.daysTo(self.user_dt) >= 1):
                    self.calc_time_diff(now)
                

            self.dt_submit.setVisible(False)
            self.render_notif(self.next_alarm_string)

    def trigger_alarm(self):
        if self.is_enabled and self.user_dt:
            now = QDateTime.currentDateTime(self.target_tz)
            if 0 <= self.user_dt.msecsTo(now) <= 1000:
                self.alarm_timer.singleShot(self.user_dt.msecsTo(now), self.alert_)



            #正直に言うと、下記のコードに対して自信があんまりないんだけどとりあえず、このままでいこうと思います。
            #必要なら次の版では更新しようとするつもりです。
            if self.frequency_ and self.frequency_ != 0:
                if self.user_dt.date().dayOfWeek() == self.frequency_ and 0 <= self.user_dt.msecsTo(now) <= 1000:
                    self.alarm_timer.singleShot(self.user_dt.msecsTo(now), self.alert_)

                
                else:
                    if 0 <= self.user_dt.msecsTo(now) <= 1000:
                        self.alarm_timer.singleShot(self.user_dt.msecsTo(now), self.alert_)


    def snooze_checker(self):
        if self.is_ringing and not self.has_snoozing:
            self.notif_.setVisible(True)
            self.notif_.setText(self.tr("スヌーズありません"))
            timer = QTimer()
            timer.setSingleShot(True)
            timer.singleShot(2000, self.clear_text)

    

    def clear_text(self):
        self.notif_.setText("")
        self.notif_.setVisible(False)

   
   
   



            


        


    def calc_time_diff(self, now):
        diff_secs = now.secsTo(self.user_dt)
        if diff_secs < 0:
            diff_secs = 0

        day = diff_secs // 86400
        hr = (diff_secs % 86400) // 3600
        mins = (diff_secs % 3600) // 60
        secs = diff_secs % 60
        

        head = self.tr("次のアラーム")
        d =self.tr("日")
        h = self.tr("時間")
        m = self.tr("分")
        s = self.tr("秒")
       

        

        self.next_alarm_string = f"{head}: {f'{day:02d} {d} ● ' if day >= 1 else ''}{hr:02d} {h} ● {mins:02d} {m} ● {secs:02d}{s}"



    

    def render_notif(self, text):
        self.notif_.setVisible(True)
        self.notif_.setText(text)
        self.notif_timer.singleShot(5000, self.hide_notif)

    

    def render_countdown(self, text):
        self.notif_.setVisible(True)
        self.notif_.setText(text)


    

    def hide_notif(self):
        self.notif_.setVisible(False)
        
        
    
    def handle_snooze(self):
        if self.is_enabled:
            if self.is_ringing and self.has_snoozing:
                    self.stop_alarm()
                    self.is_snoozing = True
                    if self.is_snoozing and self.snz_intervals > 0:
                        self.snooze_timer.start()
                        self.snooze_secs = self.snz_duration * 60
                        self.snooze_signal.emit(self.is_snoozing)
                        
                        self.snz_intervals -= 1
                        self.alarm_timer.singleShot(self.snz_duration * 60000, self.alert_)

                     
            

            
                
                



    def handle_snooze_popup(self):
        if self.snooze_popup is None and self.is_snoozing:
            self.snooze_popup = AlarmPopup(icon=self.snooze_icon, alarm_name="Zzzzz", alarm_time=self.snz_ct_str, is_alarm=False)
            self.snooze_popup.close_btn.clicked.connect(self.clear_snooze)


        self.snooze_popup.show()
        self.snooze_popup.raise_()
        self.snooze_popup.activateWindow()

    
                

            
           

    def render_snooze_timer(self):
        self.snooze_countdown()
        mins = self.snooze_secs // 60
        secs = self.snooze_secs % 60
        self.notif_.setVisible(True)
        self.snz_ct_str = f"{mins:02d}:{secs:02d}"
        self.render_countdown(self.snz_ct_str)

        if self.snooze_popup:
            self.snooze_popup.time_display.setText(self.snz_ct_str)

    def snooze_countdown(self):
        self.snooze_secs = self.snooze_secs - 1 if self.snooze_secs > 0 else 0
        if self.snooze_secs <= 0:
            self.snooze_timer.stop()
            self.hide_notif()
            self.snooze_popup.hide()
         
            



    def apply_settings(self):
        self.alarm_name = self.alarm_menu.alarm_name
        self.frequency_ = self.alarm_menu.alarm_frequency 
        self.has_snoozing = self.alarm_menu.snoozing_is_on  
        self.snz_intervals =  self.alarm_menu.snooze_count 
        self.snz_duration = self.alarm_menu.snooze_interval 
        self.alarm_cleared = False

    
    def clear_snooze(self):
        self.snz_duration = 0
        self.snz_intervals = 0
        self.is_snoozing = False
        self.alarm_cleared = True
        self.snooze_timer.stop()
        self.stop_alarm()
        self.notif_.setVisible(False)


        

            

 
    def stop_alarm(self):
        if self.is_ringing:
            self.notif_.clear()
            self.notif_.setStyleSheet("font-size: 14px; font-weight: normal;")
            self.notif_.setVisible(False)
            if not self.has_snoozing:
                self.render_notif(self.tr("アラーム停止されました"))


        self.audio_player.stop()
        self.alarm_timer.stop()
        self.is_ringing = False
        self.time_edit_.setDisabled(self.is_ringing)

       
            

        if self.alarm_popup:
            self.alarm_popup.hide()
            self.alarm_popup = None


        if self.snooze_popup:
            self.snooze_popup.hide()
            self.snooze_popup = None

      
    
               


           

           
        

        
            

    def set_enabled(self):
        self.is_enabled = not self.is_enabled
        self.alarm_on_off_btn.setIcon(self.alarm_off_icon if self.is_enabled else self.alarm_on_icon)
        self.date_edit_.setEnabled(self.is_enabled)
        self.time_edit_.setEnabled(self.is_enabled)
        self.alarm_settings_btn.setEnabled(self.is_enabled)
        self.snooze_btn.setEnabled(self.is_enabled)
        self.silence_btn.setEnabled(self.is_enabled)
        self.notif_.clear()
        self.notif_.setVisible(False)
        
        if self.audio_player.playbackState() == QMediaPlayer.PlayingState:
            self.is_ringing = False
            self.audio_player.stop()
            self.render_notif(self.tr("アラーム停止されました"))

        if not self.is_enabled:
            self.is_snoozing = False

        if self.alarm_popup:
            self.alarm_popup.hide()
            self.alarm_popup = None

        if self.snooze_popup:

            self.snooze_popup.hide()
            self.snooze_popup = None
        

            


        

    def open_settings_menu(self):
        if self.alarm_menu is None:
            self.alarm_menu = AlarmMenu()
            self.alarm_menu.alarm_tones_spin.installEventFilter(self)
            self.alarm_menu.alarm_tones_spin.valueChanged.connect(self.tone_preview)
            self.alarm_menu.submit_btn.clicked.connect(self.apply_settings)
            


        
        self.alarm_menu.show()
        self.alarm_menu.raise_()
        self.alarm_menu.activateWindow()
    


    
    def handle_alarm_popup(self):
        if self.alarm_popup is None and self.is_ringing:
            now = QDateTime.currentDateTime(self.target_tz)
            time_ = QTime(now.time().hour(), now.time().minute())
            time_str = time_.toString("HH:mm")

            self.alarm_popup = AlarmPopup(alarm_time=time_str, icon=self.alarm_icon, alarm_name=self.alarm_name, is_alarm=True)
            self.alarm_popup.snooze_btn.clicked.connect(self.handle_snooze)
            self.alarm_popup.stop_btn.clicked.connect(self.stop_alarm)

        self.alarm_popup.show()
        self.alarm_popup.raise_()
        self.alarm_popup.activateWindow()
        
            
    def tone_preview(self):
        if self.preview_allowed:
            self.audio_player.setSource(QUrl.fromLocalFile(self.alarm_menu.selected_tone_path))
            self.audio_player.play()




    def closeEvent(self, event):
        self.audio_player.stop()
        return super().closeEvent(event)
    

    def hideEvent(self, event):
        self.audio_player.stop()
        return super().hideEvent(event)
        


    

        
           
    def alert_(self):
        if not self.alarm_cleared:
            self.is_ringing = True
            self.alarm_signal.emit(self.is_ringing)
            if self.is_ringing:
                if self.alarm_menu is None or not self.alarm_menu.selected_tone_path:
                    self.audio_player.setSource(QUrl.fromLocalFile("tunes/Alarm Tones/Alarm 1.mp3"))
                else:
                    self.audio_player.setSource(QUrl.fromLocalFile(self.alarm_menu.selected_tone_path))
                   
                self.audio_player.setLoops(QMediaPlayer.Loops.Infinite)
                self.audio_player.play()
                self.time_edit_.setDisabled(self.is_ringing)

                if self.alarm_name:
                    self.notif_.setVisible(True)
                    self.notif_.setText(self.alarm_name)
                    font = QFont()
                    font.setBold(True)
                    font.setPointSize(20.0)
                    self.notif_.setFont(font)


    def mousePressEvent(self, event):
        self.stop_alarm()
        return super().mousePressEvent(event)
    

    def eventFilter(self, watched, event):
        if watched == self.alarm_menu.alarm_tones_spin:
            if event.type() == QEvent.HoverLeave:
                self.audio_player.stop()

        return super().eventFilter(watched, event)



    
class AlarmPopup(QWidget):
    def __init__(self, icon=None, alarm_time=None, alarm_name=None , is_alarm=True, has_snoozing=None):
        super().__init__()

        self.alarm_name = alarm_name
        self.alarm_time = alarm_time
        self.is_alarm = is_alarm
        self.has_snoozing = has_snoozing
        self.setWindowTitle(self.alarm_name if self.alarm_name else "⏰")
        self.setWindowIcon(icon)
        self.setFixedSize(400,400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.alarm_name_display = QLabel(text=self.alarm_name)
        self.alarm_name_display.setObjectName("almpop_label")
        self.time_display = QLabel(self.alarm_time)
        self.snooze_btn = QPushButton()
        self.stop_btn = QPushButton()
        self.close_btn = QPushButton()
    



        self.snooze_icon = QIcon(QPixmap("taima_icons/snooze_icon.png"))
        self.alarm_pause_icon = QIcon(QPixmap("taima_icons/alarm_pause_icon.png"))
        self.close_icon = QIcon(QPixmap("taima_icons/close_icon.png"))

        self.snooze_btn.setIcon(self.snooze_icon)
        self.stop_btn.setIcon(self.alarm_pause_icon)
        self.close_btn.setIcon(self.close_icon)

        self.layout_ = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.mid_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self.top_layout.addWidget(self.alarm_name_display,alignment=Qt.AlignmentFlag.AlignCenter)
        self.mid_layout.addWidget(self.time_display, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bottom_layout.addWidget(self.stop_btn)
        self.bottom_layout.addStretch(1)
        self.bottom_layout.addWidget(self.close_btn)
        self.bottom_layout.addStretch(1)
        self.bottom_layout.addWidget(self.snooze_btn)

        self.top_box = QFrame()
        self.top_box.setLayout(self.top_layout)

        self.mid_box = QFrame()
        self.mid_box.setLayout(self.mid_layout)

        self.btm_box = QFrame()
        self.btm_box.setLayout(self.bottom_layout)

        self.layout_.addWidget(self.top_box, stretch=0)
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.mid_box)
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.btm_box, stretch=0)

        self.snooze_btn.clicked.connect(self.snooze_checker)


        self.snooze_btn.setVisible(self.is_alarm)
        self.stop_btn.setVisible(self.is_alarm)
        self.close_btn.setHidden(self.is_alarm)

        
       

        self.setLayout(self.layout_)

        

    def snooze_checker(self):
        if not self.has_snoozing:
            self.alarm_name_display.setText(self.tr("スヌーズありません"))
            timer = QTimer()
            timer.setSingleShot(True)
            timer.singleShot(2000, self.clear_text)

    

    def clear_text(self):
        self.alarm_name_display.setText("")
        

        
    


     
            
            






   





class AlarmMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(QPixmap("taima_icons/settings_icon.png")))
        self.setWindowTitle(self.tr("アラーム設定"))
        self.setFixedSize(QSize(350,600))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.days = [
                    "OFF",
                    self.tr("月"),
                    self.tr("火"),
                    self.tr("水"),
                    self.tr("木"),
                    self.tr("金"),
                    self.tr("土"),
                    self.tr("日"),
                    self.tr("毎日"),
                ]

        self.tones_folder = Path("tunes/Alarm Tones")
        self.tone_paths = [path for path in sorted(list(self.tones_folder.iterdir()), key=self.get_sort_key)]

        self.tones = [path.name.split(re.search(r"\.\w+$", path.name).group())[0] for path in self.tone_paths]

        self.index_to_path = {i: str(path) for i,path in enumerate(self.tone_paths)}
        self.selected_tone_path = ''

        self.alarm_name_label = QLabel(self.tr("アラーム名"))
        self.alarm_name_label.setObjectName("alarm_label")


        self.alarm_name_input = QLineEdit(placeholderText=self.tr("朝だよ～"))
        self.alarm_name_input.setObjectName("alarm_name_edit")

        self.alarm_tones_label = QLabel(self.tr("着信音"))
        self.alarm_tones_label.setObjectName("alarm_label")

        self.alarm_tones_spin = CustomSpinBox(list_=self.tones, wrap_=True)
        self.alarm_tones_spin.setObjectName("alarm_spin")

        self.add_tone_btn = QPushButton()
        self.add_tone_btn.setIcon(QIcon(QPixmap("taima_icons/add_icon.png")))
        self.add_tone_btn.setObjectName("add_tone_btn")
        self.add_tone_btn.setFixedSize(QSize(30,30))
        

        self.alarm_frequency_label = QLabel(self.tr("繰り返し"))
        self.alarm_frequency_label.setObjectName("alarm_label")

        self.alarm_frequency_spin = CustomSpinBox(list_=self.days, wrap_=True)
        self.alarm_frequency_spin.setObjectName("alarm_spin")

        self.snooze_label = QLabel(self.tr("スヌーズ"))
        self.snooze_label.setObjectName("alarm_label")

        self.snooze_toggle = ToggleButton()
        self.snooze_toggle.setObjectName("snooze_toggle")

        self.snooze_interval_label = QLabel(self.tr("スヌーズ間隔")) #長さ
        self.snooze_interval_label.setObjectName("alarm_label")

        self.snooze_interval_spin = QSpinBox(minimum=1, maximum=30, suffix=self.tr('分'), singleStep=1, wrapping=True)
        self.snooze_interval_spin.setObjectName("alarm_spin")


        self.snooze_count_label = QLabel(self.tr("スヌーズ回数")) #スヌーズの頻度
        self.snooze_count_label.setObjectName("alarm_label")

        self.snooze_count_spin = QSpinBox(minimum=2, maximum=10, wrapping=True)
        self.snooze_count_spin.setObjectName("alarm_spin")

        self.submit_btn = QPushButton()
        self.submit_icon = QIcon(QPixmap("taima_icons/submit_icon.png"))
        self.submit_btn.setIcon(self.submit_icon)
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.setFixedHeight(50)



         # 設定初期値
        self.alarm_name = ''
        self.alarm_frequency = ''
        self.snoozing_is_on = False
        self.snooze_count = 0
        self.snooze_interval = 0



        self.snooze_count_label.setEnabled(self.snoozing_is_on)
        self.snooze_interval_label.setEnabled(self.snoozing_is_on)
        self.snooze_count_spin.setEnabled(self.snoozing_is_on)
        self.snooze_interval_spin.setEnabled(self.snoozing_is_on)


        self.wrapper1 = Wrapper(w1=self.alarm_name_label, w2=self.alarm_name_input)
        self.wrapper2 = Wrapper(w1=self.alarm_tones_label, w2=self.alarm_tones_spin, w3=self.add_tone_btn)
        self.wrapper3 = Wrapper(w1=self.alarm_frequency_label, w2=self.alarm_frequency_spin)
        self.wrapper4 = Wrapper(w1=self.snooze_label,w2=self.snooze_toggle)
        self.wrapper5 = Wrapper(w1=self.snooze_interval_label, w2=self.snooze_interval_spin)
        self.wrapper6 = Wrapper(w1=self.snooze_count_label, w2=self.snooze_count_spin)


        self.layout_ = QVBoxLayout()

        self.layout_.addWidget(self.wrapper1, stretch=1)
        self.layout_.addWidget(self.wrapper2, stretch=1)
        self.layout_.addWidget(self.wrapper3, stretch=1)
        self.layout_.addWidget(self.wrapper4, stretch=1)
        self.layout_.addWidget(self.wrapper5, stretch=1)
        self.layout_.addWidget(self.wrapper6, stretch=1)
        self.layout_.addWidget(self.submit_btn)



        self.submit_btn.clicked.connect(self.get_settings)
        self.snooze_toggle.toggled.connect(self.get_snooze_state)
        self.alarm_tones_spin.valueChanged.connect(self.on_tone_changed)
        self.add_tone_btn.clicked.connect(self.get_user_tone)
        

        self.setLayout(self.layout_)
      

    
   
           


    def is_valid_audio(self, f):
        db = QMimeDatabase()
        mime_type = db.mimeTypeForFile(f, QMimeDatabase.MatchContent)
        if mime_type.name().startswith("audio/"):
            return True

    def get_user_tone(self):
        audio_filter = "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.mpeg)"
        tone_file, _ = QFileDialog.getOpenFileName(
            self, "Selected Audio", "", audio_filter
        )
       
        if self.is_valid_audio(tone_file):
                shutil.copy(tone_file, self.tones_folder)
                self.update_tone_list()
                


    def update_tone_list(self):
            #self.tones_folder = Path("tunes/Alarm Tones")
            self.tone_paths = [path for path in sorted(list(self.tones_folder.iterdir()), key=self.get_sort_key)]
            self.tones = [path.name.split(re.search(r"\.\w+$", path.name).group())[0] for path in self.tone_paths]
            self.index_to_path = {i: str(path) for i, path in enumerate(self.tone_paths)}
            self.alarm_tones_spin.list_ = self.tones
            self.alarm_tones_spin.update()


          


    
    def get_snooze_state(self):
        self.snoozing_is_on = self.snooze_toggle.isChecked()
        self.snooze_count_spin.setEnabled(self.snoozing_is_on)
        self.snooze_interval_spin.setEnabled(self.snoozing_is_on)
        self.snooze_interval_label.setEnabled(self.snoozing_is_on)
        self.snooze_count_label.setEnabled(self.snoozing_is_on)
            

    def get_settings(self):
     
       self.alarm_name =  self.alarm_name_input.text()
       self.alarm_frequency = self.alarm_frequency_spin.value()
       if self.snoozing_is_on:
            self.snooze_count = self.snooze_count_spin.value()
            self.snooze_interval = self.snooze_interval_spin.value()
        
       self.hide()

    

    def get_sort_key(self, p):
        match = re.search(r"\d+", p.name)
        return int(match.group()) if match else 0
    


    def on_tone_changed(self, i):
        self.selected_tone_path = self.tone_paths[i]


    
    def mousePressEvent(self, event):
        return super().mousePressEvent(event)



   

    


        



  



class Wrapper(QFrame):
    def __init__(self, w1, w2, w3=None):
        super().__init__()

        self.setFrameShape(self.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout_ = QHBoxLayout()
    
        self.layout_.addWidget(w1)
        self.layout_.addStretch(3)
        self.layout_.addWidget(w2)
        if w3:
            self.layout_.addWidget(w3)
        
        self.setLayout(self.layout_)
        




    


class CustomSpinBox(QSpinBox):
    def __init__(self, list_, wrap_=True):
        super().__init__()


        self.list_ = list_
        self.wrap_ = wrap_
        self.setRange(0, len(self.list_) - 1)
        self.setWrapping(self.wrap_)
       

    def __repr__(self):
        print(len(self.list_))
        return super().__repr__()

    def textFromValue(self, val):
        return self.list_[val]
    

    def valueFromText(self, text):
        return self.list_.index(text)
    
















class ToggleButton(QCheckBox):
    def __init__(
            self,
            width = 45,
            height = 28,
            bg_color = "#565357",
            circle_color = "#F8F6F6",
            active_color =  "#5a189a" ,
            animation_curve = QEasingCurve.InOutCubic
    ):
        
        QCheckBox.__init__(self)
        self.setTristate(False)

        self.circle_width = 18

        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)
        self.ani_duration = 380

        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        self._circle_position = 4

        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(self.ani_duration)

        self.width_animation = QPropertyAnimation(self, b"circle_width", self)
        self.width_animation.setDuration(self.ani_duration)

        self.stateChanged.connect(self.start_transition)


    @Property(float)  # 念頭に置いといてアニメーションなら @Propertyにするのが鉄則です
    def circle_position(self):
        return self._circle_position


    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos 
        self.update()


    @Property(float)
    def circle_width(self):
        return self._circle_width
    
    

    @circle_width.setter
    def circle_width(self, w):
        self._circle_width = w
        self.update()



    #状態確認執行官ｗ
    def start_transition(self, value):
        self.animation.stop()
        self.animation.setStartValue(self.circle_position)
      
        
        if value:
            self.animation.setEndValue(self.width() - 21)

        else:
            self.animation.setEndValue(4)  # 元通りにする
          


        self.width_animation.setKeyValueAt(0,18)
        self.width_animation.setKeyValueAt(0.5, 24)
        self.width_animation.setKeyValueAt(1,18)

        self.animation.start()
        self.width_animation.start()
        
        
        



        


    
       

    #ボタンのクリック面を広がる
    def hitButton(self, pos):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)


        p.setPen(Qt.NoPen)
        rect = QRect(0,0, self.width(), self.height())


        if self.isChecked():
            p.setBrush(QColor(self._active_color))

        else:
            p.setBrush(QColor(self._bg_color))
          
        
        p.drawRoundedRect(rect, self.height() // 2, self.height() // 2)

        #p.setBrush(QColor(self._active_color))
        self._circle_color = '#e0aaff' if self.isChecked() else '#F8F6F6'
        p.setBrush(QColor(self._circle_color))
        
        # xcor -> ycor -> width -> height
        p.drawEllipse(self.circle_position, 4, self.circle_width, 18)
        
        p.end()
