from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, QTimeZone, QUrl, QLocale, QTranslator
from PySide6.QtGui import QIcon, QPixmap
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

)

from PySide6.QtGui import QIntValidator
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import sys






class Clock(QWidget):
    def __init__(self):
        super().__init__()

        self.clock_ = QTimer()
        self.clock_.start(1000)

        # render the time based on the user's system
        self.user_timezone_id = QTimeZone.systemTimeZoneId()
       
        self.days_ = [self.tr("月"),self.tr("火"),self.tr("水"),self.tr("木"),self.tr("金"),self.tr("土"),self.tr("日")]
        
        
        #self.tz_id = QTimeZone.availableTimeZoneIds(QLocale.Country.Japan) - used to get the available time zone id for a particular country

        #set the IANA id to the the timezone id retrieved above
        self.target_tz = QTimeZone(self.user_timezone_id)
       
    
        self.datetime_ = QDateTime()
        self.time_display_ =  QLabel()
        
        self.date_display_ = QLabel()
     
        self.layout_ = QHBoxLayout(self)

        self.clock_layout = QHBoxLayout()
        self.date_layout = QHBoxLayout()

        self.clock_box= QFrame()
        self.date_box = QFrame()

        self.clock_layout.addWidget(self.time_display_, alignment=Qt.AlignmentFlag.AlignCenter)
        self.clock_box.setLayout(self.clock_layout)
        

        self.date_layout.addWidget(self.date_display_)
        self.date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_box.setLayout(self.date_layout)

        self.layout_.addWidget(self.clock_box)
        self.layout_.addSpacing(10)
        self.layout_.addWidget(self.date_box)
        #self.layout_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.clock_.timeout.connect(self.update_time)
        self.date_display_.setObjectName("date_")
        self.time_display_.setObjectName("time_")

        


        self.time_display_.setFixedSize(QSize(210,50))


        self.setLayout(self.layout_)






    def update_time(self):
       current_dt = QDateTime.currentDateTime(self.target_tz)
       #day_value = current_date.dayOfWeek()
       #today = self.days_[day_value - 1]
       self.time_display_.setText(current_dt.toString("HH:mm:ss"))
       date_str = QLocale.system().toString(current_dt.date(), QLocale.LongFormat)
       self.date_display_.setText(date_str)

       #self.date_display_.setText(current_dt.toString("yyyy 年 MM 月 dd 日 ") + f"({today})" )

        

class Pomodoro(QWidget):
    #25.0分ごとに5.0分の小休憩が行い、最大4回まで.つまり、作業中の後に休憩


    #4回目で長休憩が行い、継続時間は15.0分

    def __init__(self):
        super().__init__()
        self.title_ = self.tr("ポモドーロ")
        self.setWindowTitle(self.title_)
        self.resize(300,300)
        self.display_ = QLineEdit(text="25:00")
        self.session_label = QLabel(self.tr("作業開始"))
        self.session_indicator = QLabel(self.tr("始めよう"))

        self.edit_pix = QPixmap("taima_icons/edit_icon.png")
        self.play_pause_pix = QPixmap("taima_icons/play_pause.png")
        self.play_pix = QPixmap("taima_icons/play_arrow_icon.png")
        self.pause_pix = QPixmap("taima_icons/pause_icon.png")
        self.restart_pix = QPixmap("taima_icons/restart_icon.png")
        self.stop_pix = QPixmap("taima_icons/stop_icon.png")

        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.audio_player.setAudioOutput(self.audio_output)




        self.play_pause_icon = QIcon(self.play_pause_pix)
        self.edit_icon = QIcon(self.edit_pix)
        self.play_icon = QIcon(self.play_pix)
        self.pause_icon = QIcon(self.pause_pix)
        self.restart_icon = QIcon(self.restart_pix)
        self.stop_icon = QIcon(self.stop_pix)
        


        self.edit_btn = QPushButton() #時間の頻度を自由に設定できる
        self.stop_btn = QPushButton() #全部クレアする
        self.restart_btn = QPushButton()
        self.start_pause_btn = QPushButton()
        self.edit_menu = EditWindow()
        self.work_mins = 25
        self.long_break_mins=15
        self.short_break_mins = 5
        self.work_state = self.tr("作業中")
        self.short_break_state = self.tr("小休憩")
        self.long_break_state = self.tr("長休憩")
        self.paused_state = self.tr("一時中止")
        self.stopped_state = self.tr("終了")
        self.session_states = [self.work_state, self.short_break_state, self.long_break_state, self.paused_state, self.stopped_state]

        self.values = []
        

        self.session_secs = self.work_mins * 60 # 秒の数え管理者
        self.is_resting = False
        self.is_over = False

        
        
        self.session_count = 1


        self.session_max = 4
        self.mm = 0
        self.ss = 0
        self.session_state = self.session_states[-1]

        #self.break_tally_secs = 0
        self.is_running = False
        #self.cycle_tracker = 0# サイクルの数え管理   
        #self.display_container = QFrame()
        
        #self.display_con_layout = QVBoxLayout()
        #self.display_con_layout.addWidget(self.session_indicator, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        #self.display_con_layout.addWidget(self.display_, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        #self.display_container.setLayout(self.display_con_layout)


        self.helper_box = QFrame()
        self.helper_layout = QHBoxLayout()
        self.helper_layout.addWidget(self.edit_btn)
        self.helper_layout.addWidget(self.session_label, alignment= Qt.AlignmentFlag.AlignCenter)
        self.helper_layout.addWidget(self.stop_btn)
        self.helper_box.setLayout(self.helper_layout)
      


        self.layout_ = QGridLayout()
        self.display_.setFixedWidth(500)
       
        
        

        #self.layout_.addWidget(self.session_indicator, 0,1)
        self.layout_.addWidget(self.session_indicator, 0,1, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.layout_.addWidget(self.display_, 1,1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout_.addWidget(self.start_pause_btn, 3, 0)
        self.layout_.addWidget(self.helper_box, 3,1)
        self.layout_.addWidget(self.restart_btn, 3, 2)

        # By manually setting the stretch factor of the rows you can not only control the distribution of the 
        # rows but also enforce the layout of an element as shown below

        self.layout_.setRowStretch(0, 1)  
        self.layout_.setRowStretch(1, 0)  
        self.layout_.setRowStretch(2, 1)  # added blank row to prevent the display sticking to the bottom
        self.layout_.setRowStretch(3, 0)

        

        self.display_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
  



        self.time_handler = QTimer()
        self.time_handler.setInterval(1000)
        

        #self.session_handler = QElapsedTimer()
        self.start_pause_btn.setFixedSize(QSize(75,60))
        self.restart_btn.setFixedSize(QSize(75,60))
        self.edit_btn.setFixedSize(QSize(75,60))
        self.stop_btn.setFixedSize(QSize(75,60))

        self.start_pause_btn.setObjectName("pomo_btn")
        self.restart_btn.setObjectName("pomo_btn")
        self.edit_btn.setObjectName("pomo_btn")
        self.stop_btn.setObjectName("pomo_btn")

        self.session_label.setObjectName("pomo_sess_display")
        #self.display_.setObjectName("pomo_display")
        self.session_indicator.setObjectName("pomo_indi")


        self.stop_btn.setIcon(self.stop_icon)
        self.restart_btn.setIcon(self.restart_icon)
        self.start_pause_btn.setIcon(self.play_pause_icon)
        self.edit_btn.setIcon(self.edit_icon)

        

        #ボタンの繋ぎ
        self.time_handler.timeout.connect(self.countdown)
        self.start_pause_btn.clicked.connect(self.start_pause)
        self.restart_btn.clicked.connect(self.restart_)
        self.edit_btn.clicked.connect(self.open_edit_menu)
        self.stop_btn.clicked.connect(self.stop_)
        self.edit_menu.submit_button.clicked.connect(self.get_user_inputs)
        self.edit_menu.submit_button.clicked.connect(self.close_edit_menu)

        self.display_.setReadOnly(True)
        self.setLayout(self.layout_)





    def alert_(self):
            self.audio_player.setSource(QUrl.fromLocalFile("tunes/Alarm Tones/Alarm 2.mp3"))
            self.audio_player.setLoops(QMediaPlayer.Loops.Infinite)
            self.audio_player.play()



    def countdown(self):
       
        if self.session_secs > 0:
            self.session_secs -= 1


            
            
        
        if self.session_secs == 0 and not self.is_over: # if we've justed finished a work session

            if not self.is_resting:  # and not started our break
                if self.session_count < self.session_max:  # if we still have work sessions left
                    self.session_state = self.session_states[1]  # break
                    self.session_secs = self.short_break_mins * 60 # set the timer for the break session
                    
            

                else:   # if we've completed all of our work sessions 
                    self.is_over = True # then we declare that we're done
                   
                    self.session_indicator.setText(self.tr("よくやったな、ごゆっくり休憩しなさい"))  # we encourage the user lol
                    self.session_state = self.session_states[2]  # set the long break state
                    self.session_secs = self.long_break_mins * 60 # and set the timer for the long break

                self.is_resting = True # toggle the resting state before incrementing the timer
            
            
                
                #["作業中","小休憩","長休憩","一時中止","終了"]
            else:  # if we've finished out break 
                # if we've ended a long break then we restart the session counter  otherwise we move on to the next session
                self.session_count = 1 if self.session_state == self.session_states[2] else self.session_count + 1

                self.session_secs = self.work_mins * 60  # set the timer for the work session
                self.session_state = self.session_states[0] # set the work state
                self.is_resting = False # alert the program that we're no longer resting

        self.session_label.setText(self.session_state)

        if not self.is_over:
            # as long as the timer is running show the current session along with the total number of sessions

            self.start_pause_btn.setEnabled(True)
            self.session_indicator.setText(f"{self.session_count} / {self.session_max}")
            

            # otherwise end the timer
        if self.is_over and self.session_secs == 0:
            self.alert_()
            self.is_running = False
            self.time_handler.stop()
            self.start_pause_btn.setEnabled(False)
            self.session_indicator.setText(self.tr("お疲れ様でした"))
            self.start_pause_btn.setIcon(self.play_pause_icon)
            self.session_label.setText(self.tr("期間終了"))
        
        self.format_time()
  
        

    def format_time(self):
        self.mm = self.session_secs // 60
        self.ss = self.session_secs % 60
        self.display_.setText(f"{self.mm:02d}:{self.ss:02d}")
       



    
    def start_pause(self):
        self.is_running = not self.is_running
        #["作業中","小休憩","長休憩","一時中止","終了"]

        if not self.is_running:
            self.time_handler.stop()
            self.session_state = self.session_states[3]
            self.start_pause_btn.setIcon(self.play_icon)
         
            
            #self.start_pause_btn.setIcon(self.pause_icon)
        else:
            self.time_handler.start()

            self.restart_btn.setEnabled(True)
            self.start_pause_btn.setIcon(self.pause_icon)
            #self.session_handler.start()
            self.session_state = self.session_state if self.session_state in (self.session_states[1], self.session_states[2]) else self.session_states[0]
            #self.start_pause_btn.setIcon(self.pause_icon)

        self.session_label.setText(self.session_state)
       


    def restart_(self):
        self.time_handler.stop()
        self.start_pause_btn.setEnabled(True)
        self.is_over = False
        self.is_running = False
        self.is_resting = False
        self.session_count = 1
        self.session_secs = self.work_mins * 60
        
    
        self.session_state = self.session_states[0]
        self.session_max = self.session_max
        self.session_label.setText(self.session_state)
        self.session_indicator.setText(self.tr("作業開始"))
        self.start_pause_btn.setIcon(self.play_pause_icon)
        self.display_.setText(f"{self.work_mins:02d}:00")
    
        
        


    def stop_(self):
        self.time_handler.stop()
        self.audio_player.stop()
        self.is_running = False

        self.session_label.setText(self.tr("作業開始"))
        self.session_indicator.setText(self.tr("始めよう"))
        
        self.session_count = 1
        self.session_secs = self.work_mins * 60
        self.restart_btn.setEnabled(False)
        self.display_.setText(f"{self.work_mins:02d}:00")
        self.start_pause_btn.setIcon(self.play_pause_icon)
        self.session_indicator.setText("1")



    def open_edit_menu(self):
        if self.edit_menu is None:
            self.edit_menu = EditWindow()
            
        self.edit_menu.show()
        self.edit_menu.raise_()
        self.edit_menu.activateWindow()



    def get_user_inputs(self):
        self.values = self.edit_menu.submit_()
        if self.values and all(i != 0 for i in self.values):
            self.work_mins = int(self.values[0])
            self.short_break_mins = int(self.values[1])
            self.long_break_mins= int(self.values[2])
            self.session_max = int(self.values[-1])

            self.stop_()






    def close_edit_menu(self):
        if self.values and all(i != 0 for i in self.values):
            self.edit_menu.hide()


    
    def mousePressEvent(self, event):
        if self.audio_player.playbackState() == QMediaPlayer.PlayingState:
            self.audio_player.stop()

        return super().mousePressEvent(event)




    
    
    





"""
  def getInputs(self):
        if all(i.hasAcceptableInput() for i in self.inputs):
            self.values = [x.text() for x in self.inputs]
            self.warning.setVisible(False)


        else:
            self.warning.setVisible(True)

    

    def submit_(self):
        self.getInputs()
        

"""


class EditWindow(QWidget):
    def __init__(self):
        super().__init__()


        self.title_ = self.tr("ポモドーロ設定")
        self.setWindowTitle(self.title_)
        self.setWindowIcon(QIcon(QPixmap("taima_icons/settings_icon.png")))
        self.setFixedSize(QSize(300,500))

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        

        # Remember to use a validator
        self.validator_ = QIntValidator(1,60, self) 
        self.short_validator =  QIntValidator(0,60, self)

        
        self.instructions = QLabel(self.tr("お好みの期間数を入力してください"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.warning = QLabel(
            text=self.tr("申し訳ございません、小休憩以外が各期間の許可される長さは1ー60ですので再試行してください。"),
            alignment=Qt.AlignmentFlag.AlignCenter,
            )
        self.instructions.setWordWrap(True)
        self.warning.setWordWrap(True)
       

        
        self.instructions.setObjectName("pomo_instructions")
        self.warning.setObjectName("pomo_warning")
        

        self.work_edit_label = QLabel(text=self.tr("作業"))
        self.work_edit_label.setObjectName("pomo_edit_label")


        self.work_edit_field = QLineEdit(text="25", placeholderText="25")
        self.work_edit_field.setObjectName("pomo_input_field")

        self.break_edit_label_s = QLabel(self.tr("小休憩"))
        self.break_edit_label_s.setObjectName("pomo_edit_label")


        self.break_edit_field_s = QLineEdit(text="5", placeholderText="5")
        self.break_edit_field_s.setObjectName("pomo_input_field")


        self.break_edit_label_l = QLabel(self.tr("長休憩"))
        self.break_edit_label_l.setObjectName("pomo_edit_label")

        self.break_edit_field_l = QLineEdit(text="15", placeholderText="15")
        self.break_edit_field_l.setObjectName("pomo_input_field")

        self.session_limit_label = QLabel(self.tr("期間数"))
        self.session_limit_label.setObjectName("pomo_edit_label")

        self.session_limit_field = QLineEdit(text="4", placeholderText="4")
        self.session_limit_field.setObjectName("pomo_input_field")

        self.submit_icon = QIcon(QPixmap("taima_icons/submit_icon.png"))
        self.submit_button = QPushButton()
        self.submit_button.setIcon(self.submit_icon)
        self.submit_button.setObjectName("submit_btn")
        self.submit_button.setFixedHeight(50)
        

        

        
        

        self.values = [] # contains all the inputs entered by the user once validated
 

        self.layout_ = QVBoxLayout()

        self.layout_.addWidget(self.instructions)
        self.layout_.addSpacing(2)
        self.layout_.addWidget(self.warning)

        self.layout_.addStretch(3)
        self.layout_.addWidget(self.work_edit_label)
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.work_edit_field)
        self.layout_.addStretch(3)

        self.layout_.addWidget(self.break_edit_label_s)
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.break_edit_field_s)
        self.layout_.addStretch(3)


        self.layout_.addWidget(self.break_edit_label_l)
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.break_edit_field_l)
        self.layout_.addStretch(3)


        self.layout_.addWidget(self.session_limit_label)
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.session_limit_field)
        self.layout_.addStretch(3)


        self.layout_.addWidget(self.submit_button)
        


        self.setLayout(self.layout_)
        self.warning.setVisible(False)

        self.inputs = self.findChildren(QLineEdit)
        for i in self.inputs:
            i.setValidator(self.validator_)
        

        # in case the user doesn't want to break
        self.break_edit_field_s.setValidator(self.short_validator)

   

    def getInputs(self):
        self.values = [] #need to reset the values from the previous session otherwise we'll bypass the validator as it will use the values from the previous session
        if all(i.hasAcceptableInput() for i in self.inputs):
            self.values = [x.text() for x in self.inputs]
            self.warning.setVisible(False)


        else:
            self.warning.setVisible(True)

    

    def submit_(self):
        self.getInputs()
        if self.values:
           return self.values
        




    













        