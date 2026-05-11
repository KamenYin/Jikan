from PySide6.QtCore import Qt, QUrl ,QTimer, QSize, QRegularExpression, QElapsedTimer
from PySide6.QtGui import  QRegularExpressionValidator,QKeyEvent,QIcon, QPixmap
from PySide6.QtWidgets import (
    QLineEdit,
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QSizePolicy
)

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput







class Timer(QWidget):
    def __init__(self):
        super().__init__()

        # define basic layout of the window and set a custom size based on the dimensions of the system
        self.is_running = False  # Flag indicating the current state of the timer
        self.initial_time = [] # contains the initial input entered by the user # Flag to confirm whether or not the original input has been entered by the user
        self.timer_layout = QGridLayout()
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.audio_player.setAudioOutput(self.audio_output)
        self.is_ringing = False



        

        # define the button icons by creating a QPixmap object for each
       
        self.play_pix = QPixmap("taima_icons/play_arrow_icon.png")
        self.pause_pix = QPixmap("taima_icons/pause_icon.png")
        
        self.restart_pix = QPixmap("taima_icons/restart_icon.png")
        self.plus_pix = QPixmap("taima_icons/plus_icon.png")
        self.minus_pix = QPixmap("taima_icons/minus_icon.png")
        #self.icon_size = self.timer_pix.size()
        
        

        # create a QIcon object using the QPixmap objects define above
        
        self.restart_icon = QIcon(self.restart_pix)
        self.play_icon = QIcon(self.play_pix)
        self.pause_icon = QIcon(self.pause_pix)
        self.plus_icon = QIcon(self.plus_pix)
        self.minus_icon = QIcon(self.minus_pix)


        # initializing the timer:

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.remaining_secs = 0

        # define the widgets to be used
        # update instead of using a single QLineEdit for the timer 
        # to improve the UX I'll use a 3 separate inputs i.e.
        # HH : MM : SS that the user doesn't need to retype the entire string
        # and will only be concerned with filling in the respective values

        # I'll start by defining a frame which will act as the container for the necessary widgets
        # i.e. 3 QLineEdits and 2 labels

        # parent container 
        self.time_container = QFrame(self) 
        self.plus_minus_box = QFrame(self)
        
        # Added a QLabel that'll render when time's up

        self.notif_ = QLabel(self.tr("時間です！"))
        self.notif_.setObjectName("timesup")
        self.notif_.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.instructions = QLabel(self.tr("クリックして停止"))
        self.instructions.setObjectName("instr")
        self.instructions.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setStyleSheet("QLabel#timesup {font-family:'Rampart One'; font-size:24px; font-weight:light; ;} QLabel#instr {font-family:'Revalia'; font-size:12px; }")

        self.top_box = QFrame()
        self.top_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.top_box.setFixedHeight(65)
      
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.notif_ ,alignment=Qt.AlignmentFlag.AlignCenter)
        self.top_layout.addWidget(self.instructions, alignment=Qt.AlignmentFlag.AlignCenter)
        self.top_box.setLayout(self.top_layout)


        # children opted to create the fields pythonically instead of manually to control the tabbing/backspace events
        self.fields = []
        self.time_rgx = QRegularExpression("[0-5][0-9]") 
        self.is_valid = False

        for field in range(3):
            field = TimeField(placeholderText="00")
            field.setMaxLength(2)
            field.setAlignment(Qt.AlignmentFlag.AlignRight)
            # Switched from QIntValidator to QRegularExpression as while it enforced a specific numerical range, it didn't enforce  '00' which would break the code
            field.setValidator(QRegularExpressionValidator(self.time_rgx, self))
            field.setLayoutDirection(Qt.RightToLeft)
            #field.setCursorMoveStyle(Qt.VisualMoveStyle)

            self.fields.append(field)

        # goes through the array containing the QLineEdit instances 
        # and checks to see if the input requirements have been satisfied 
        # starting with the last field in the array i.e.:
        #  <----------------
        #  [ [HH]:[MM]:[SS] ]
                                                        
        self.fields[2].textChanged.connect(lambda:self.check_fields(2,1))
        self.fields[1].textChanged.connect(lambda:self.check_fields(1,0))
    

        self.sep1 = QLabel(":")
        self.sep2 = QLabel(":")

        # minimal styling of the container
    
        self.time_container.setFixedWidth(500)
        self.time_container.setObjectName("timer_box")

       
        # defining it's layout
        self.time_container_layout = QHBoxLayout(self.time_container)
        self.time_container_layout.addWidget(self.fields[0])
        self.time_container_layout.addWidget(self.sep1)
        self.time_container_layout.addWidget(self.fields[1])
        self.time_container_layout.addWidget(self.sep2)
        self.time_container_layout.addWidget(self.fields[2])
        self.time_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)






        self.play_pause_btn = QPushButton()
        self.restart_btn = QPushButton()
       
        self.plus_btn = QPushButton()
        self.minus_btn = QPushButton()

        # Assign the icons to the respective buttons
        
        self.restart_btn.setIcon(self.restart_icon)
        self.play_pause_btn.setIcon(self.play_icon)
        self.plus_btn.setIcon(self.plus_icon)
        self.minus_btn.setIcon(self.minus_icon)


        self.plus_btn.setObjectName("min_toggle")
        self.minus_btn.setObjectName("min_toggle")

     
        


        self.plus_minus_box.setFrameStyle(QFrame.NoFrame)
        self.plus_minus_layout = QHBoxLayout(self.plus_minus_box)
        self.plus_minus_layout.addWidget(self.plus_btn)
        self.plus_minus_layout.addWidget(self.minus_btn)



        # configure the layout i.e. 3 x 3 grid
        self.timer_layout.addWidget(self.top_box, 0,1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.timer_layout.addWidget(self.time_container, 2,1)  # center
        self.timer_layout.addWidget(self.plus_minus_box, 4,1) #bottom center
        self.timer_layout.addWidget(self.play_pause_btn, 4,0, alignment=Qt.AlignmentFlag.AlignLeft) #bottom left
        self.timer_layout.addWidget(self.restart_btn, 4,2, alignment=Qt.AlignmentFlag.AlignRight)  # bottom right


        self.timer_layout.setRowStretch(0,0)
        self.timer_layout.setRowStretch(1,1)
        self.timer_layout.setRowStretch(3,2)
      
      
        # set the tab order for the respective widgets

        self.setTabOrder(self.fields[-1], self.fields[1])
        self.setTabOrder(self.fields[1], self.fields[0])


        # connecting the signals

       


        self.plus_btn.setFixedSize(QSize(100,50))
        self.minus_btn.setFixedSize(QSize(100,50))

       
        
        self.fields[0].editingFinished.connect((self.handle_time))
        self.fields[1].editingFinished.connect((self.handle_time))
        self.fields[2].editingFinished.connect((self.handle_time))

        



        self.fields[0].editingFinished.connect((self.get_original_values))
        self.fields[1].editingFinished.connect((self.get_original_values))
        self.fields[2].editingFinished.connect((self.get_original_values))

        self.all_entries = self.findChildren(QLineEdit)
        for entry in self.all_entries:
            entry.selectionChanged.connect(lambda e=entry: e.deselect())

        self.restart_btn.clicked.connect(self.restart_timer)
        self.plus_btn.clicked.connect(self.add_time)
        self.minus_btn.clicked.connect(self.minus_time)
      

        self.timer.timeout.connect(self.tick)
        self.play_pause_btn.clicked.connect(self.play_pause)
        self.notif_.setVisible(False)
        self.instructions.setVisible(False)

        self.setLayout(self.timer_layout)
       

    # Things to consider when implementing the timer
    # getting a hold of the user's input 
    # formatting the input in standard time format
    # handling the calculations for hrs, minutes , seconds
    # making the timer 'tick' per second
    # rendering the timer to the screen
    # keep track of  the state of the timer i.e. if it's running/paused
    # handling the event accordingly depending on the state of the timer.
    def pad_fields(self):
        for field in self.fields:
            if not field.text():
                field.setText("00")
                
            if len(field.text()) == 1:
                field.setText(f"{int(field.text()):02d}")
        

    def get_original_values(self):
        # this should only run on the first instance of the timer being run
        # and will only be reset after the user hits reset i.e. "captures a new save point"
        if not self.is_running:
            self.initial_time = [field.text() if field.text() else "00" for field in self.fields]
            self.has_originals = True

            #print(self.initial_time)

        



    def handle_time(self):
        # first get the user input from the respective fields
        # check to see if any fields are empty if so pad the field accordingly
        # i.e. if theres nothing '00' if there's only 1 pad it with a 0 xx.2d
        # In order for the reset to function i need a way to not only get the original values
        # but also ensure that they don't change so I suspect one way to do this would be to
        
        if self.is_ringing:
            self.is_ringing = False
            self.audio_player.stop()
        # setting the values in a variable called originals and if it's != to said values do nothing
        if not self.is_running:
            self.pad_fields()
        
            self.hh = int(self.fields[0].text()) 
            self.mm = int(self.fields[1].text()) 
            self.ss = int(self.fields[2].text()) 
            
            self.remaining_secs = (self.hh * 3600) + (self.mm * 60 ) + self.ss 
            
            print(f"Handle Time: {self.remaining_secs}")
            self.format_time()


    def add_time(self):
        print(f"Before: {self.remaining_secs}")
        if not self.is_running:
            self.remaining_secs += 60
            self.format_time()
     
      
            print(f"After: {self.remaining_secs}")

    def minus_time(self):
        if not self.is_running:
            print(f"Before: {self.remaining_secs}")
            self.remaining_secs = self.remaining_secs - 60 if self.remaining_secs >= 60 else 0
            self.format_time()
        
            print(f"After: {self.remaining_secs}")
        


    def check_fields(self, current_idx, target_idx):    
        if self.fields[current_idx].hasAcceptableInput():
            self.fields[target_idx].setFocus()
            self.fields[target_idx].selectAll()

    
    def format_time(self):
        self.hh = self.remaining_secs // 3600
        self.mm = (self.remaining_secs % 3600) // 60
        self.ss = self.remaining_secs % 60

        self.fields[0].setText(f"{self.hh:02d}")
        self.fields[1].setText(f"{self.mm:02d}")
        self.fields[2].setText(f"{self.ss:02d}")
    

       
    def restart_timer(self):
        if self.is_running:
            self.is_running = False
            self.timer.stop()

        if self.remaining_secs > 0:
                self.play_pause_btn.setIcon(self.play_icon)
                self.fields[0].setText(f"{int(self.initial_time[0]):02d}")
                self.fields[1].setText(f"{int(self.initial_time[1]):02d}")
                self.fields[2].setText(f"{int(self.initial_time[2]):02d}")

        else:
            self.fields[0].setText(f"00")
            self.fields[1].setText(f"00")
            self.fields[2].setText(f"00")
        
    
        



    def play_pause(self):
        self.is_running = not self.is_running
        if self.is_running and self.remaining_secs > 0:
            self.timer.start()
            self.play_pause_btn.setIcon(self.pause_icon)
           
        else:
            self.timer.stop()
            self.play_pause_btn.setIcon(self.play_icon)
           
        
        for field in self.fields:
            field.setReadOnly(self.is_running)


    
    def tick(self):
        if self.remaining_secs <= 0:
            self.alert_()
            self.is_ringing = True
            self.timer.stop()
            self.is_running = False
            self.play_pause_btn.setIcon(self.play_icon)
            for field in self.fields:
                field.setReadOnly(self.is_running)
          

        else:
            self.remaining_secs -= 1
            
        print(f"Current total seconds: {self.remaining_secs}")
        self.format_time()


    def alert_(self):
        self.audio_player.setSource(QUrl.fromLocalFile("tunes/Alarm Tones/Alarm 6.mp3"))
        self.audio_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.audio_player.play()
        self.render_notif()


    
    def render_notif(self):
        self.notif_.setVisible(True)
        self.instructions.setVisible(True)
        

    def hide_notif(self):
        self.notif_.setVisible(False)
        self.instructions.setVisible(False)
    

        

    


    def set_styles(self):

        styles = f"""

        QFrame#timer_box{{
            display: flex;
            justify-content:center;
            align-items:center;
            gap:0;
        }}




"""
        
        self.setStyleSheet(styles)



    def mousePressEvent(self, event):
        if self.audio_player.playbackState() == QMediaPlayer.PlayingState:
            self.audio_player.stop()
        
        self.hide_notif()
        return super().mousePressEvent(event)

  





class TimeField(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        


    def keyPressEvent(self, event:QKeyEvent):
      if event.key() == Qt.Key_Backspace and not self.text():
          self.focusNextPrevChild(True)

      super().keyPressEvent(event)







class StopWatch(QWidget):
    def __init__(self):
        super().__init__()
    
        self.is_counting = False  # Flag indicating the current state of the stpopwatch
        self.timer_ = QTimer(self)
        self.play_pix = QPixmap("taima_icons/timer_play_icon.png")
        self.pause_pix = QPixmap("taima_icons/timer_pause_icon.png")
        self.restart_pix = QPixmap("taima_icons/restart_icon.png")
        self.stop_pix = QPixmap("taima_icons/stop_icon.png")
        self.flag_pix = QPixmap("taima_icons/flag_icon.png")



        # keep a reference to the variables to be displayed/used :
        self.total_centisecs = 0
        self.paused_time = 0
        self.hh_=0
        self.mm_=0
        self.ss_=0
        self.cs_=0
    
  

        # create a QIcon object using the QPixmap objects define above
        
        self.restart_icon = QIcon(self.restart_pix)
        self.play_icon = QIcon(self.play_pix)
        self.pause_icon = QIcon(self.pause_pix)
        self.stop_icon = QIcon(self.stop_pix)
        self.flag_icon = QIcon(self.flag_pix)

        # initializing the timer:

        self.elapsed_timer = QElapsedTimer()
        self.total_centisecs = 0

        # initializing the flag container
        self.flag_box = []


        self.flag_display = QLabel("")
        self.flag_display.setFixedHeight(60)
        self.flag_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
 

        # parent container 
       
        self.control_box = QFrame()
        
        self.display_ = QLabel(text="00.00")
        self.display_.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_.setFixedHeight(90)
      


        self.is_valid = False
     
        self.display_.setObjectName("stopwatch_display")


        self.pause_play_btn = QPushButton()
        self.restart_btn = QPushButton()
        self.flag_btn = QPushButton()
        self.stop_btn = QPushButton()
        

        # Assign the icons to the respective buttons
        
        self.restart_btn.setIcon(self.restart_icon)
        self.pause_play_btn.setIcon(self.play_icon)
        self.flag_btn.setIcon(self.flag_icon)
        self.stop_btn.setIcon(self.stop_icon)

        self.flag_btn.setFixedSize(QSize(100,50))
        self.stop_btn.setFixedSize(QSize(100,50))


        self.flag_btn.setObjectName("min_toggle")
        self.stop_btn.setObjectName("min_toggle")
        self.flag_display.setObjectName("flag_display")

        
        self.box_layout = QHBoxLayout()
    
        self.box_layout.addWidget(self.flag_btn)
        self.box_layout.addWidget(self.stop_btn)
        self.control_box.setLayout(self.box_layout)

        self.bottom = QFrame()
        self.btm_layout = QHBoxLayout()
        self.btm_layout.addWidget(self.pause_play_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.btm_layout.addWidget(self.control_box)
        self.btm_layout.addWidget(self.restart_btn, alignment=Qt.AlignmentFlag.AlignRight)  

        self.bottom.setLayout(self.btm_layout)





        self.watch_layout = QVBoxLayout()
        
      
        self.watch_layout.addWidget(self.flag_display, 0)
        self.watch_layout.addStretch(1)
        self.watch_layout.addWidget(self.display_, 0)
        self.watch_layout.addStretch(2)
        self.watch_layout.addWidget(self.bottom, 0)

            
        self.restart_btn.clicked.connect(self.restart_)
        self.flag_btn.clicked.connect(self.capture_the_flag)
        self.stop_btn.clicked.connect(self.stop_)
      
        self.pause_play_btn.clicked.connect(self.pause_play)
        self.timer_.timeout.connect(self.counter_)
        

        self.setLayout(self.watch_layout)


    


    def counter_(self):
        # based on the total number of secs the display will change
        # i.e. from SS.mm -> MM:SS.mm -> HH:MM:SS.mm 

        if self.is_counting:
            current = self.elapsed_timer.elapsed()
            self.total_centisecs = (self.paused_time + current) // 10


            self.hh_ = (self.total_centisecs // 360000) 
            self.mm_ =  (self.total_centisecs // 6000) % 60
            self.ss_ =   (self.total_centisecs // 100) % 60
            self.cs_ =    self.total_centisecs % 100
            
            # The following attempts to render the values to the display based on the value of self.total_centisecs 
            # i.e. if the value is too small to render an hour  (<3600) / minute (<60) only show the seconds and centiseconds (all with '00 padding)
            self.time_string = f"{f'{self.hh_:02d}:'if self.total_centisecs >= 360000 else ''}{f'{self.mm_:02d}:' if self.total_centisecs >= 6000 else ''}{self.ss_:02d}.{self.cs_:02d}"
            #print(self.time_string)


            self.display_.setText(self.time_string)

        

   
    


    def stop_(self):
        self.is_counting = False
        self.timer_.stop()
        self.elapsed_timer.invalidate()
        self.total_centisecs = 0
        self.paused_time = 0
        self.pause_play_btn.setIcon(self.play_icon)
        self.display_.setText("00.00")
        self.flag_box = []
        self.flag_display.clear()
       
      





    def capture_the_flag(self): 

        if self.is_counting:
            flag = self.display_.text()
            if len(self.flag_box) <= 6:
                self.flag_box.append(flag)

                flags = ' '.join(self.flag_box)
                cleaned_flags = [x for x in flags.split(" ")]
                flag_string = ' '.join([f'#{pos+1}. {flag}' for pos, flag in enumerate(cleaned_flags)])

                self.flag_display.setText(flag_string)

            


    
    def pause_play(self):
        self.is_counting = not self.is_counting
        if self.is_counting:
            self.elapsed_timer.start()
            self.timer_.start(10)
            self.pause_play_btn.setIcon(self.pause_icon)
            if  self.flag_display.isHidden():
                self.flag_display.setHidden(False)
            


        else:
            self.paused_time += self.elapsed_timer.elapsed()
            self.timer_.stop()
            self.pause_play_btn.setIcon(self.play_icon)

        

        



    def restart_(self):
        self.is_counting = False
        self.timer_.stop()
        self.total_centisecs = 0
        self.paused_time = 0
        self.hh_=0
        self.mm_=0
        self.ss_=0
        self.cs_=0
        self.pause_play_btn.setIcon(self.play_icon)
        self.elapsed_timer.invalidate()
        self.display_.setText("00.00")
        self.flag_box = []





#アニメーションのコンセプトしっかり身についたら直すつもりです。
class FlagWindow(QWidget):
    def __init__(self, flags):
        super().__init__()

        self.setFixedSize(300, 100)
        self.flags = flags
        self.x_offset = 0
        self.belt_ = []
        self.engine_ = QTimer()
        self.engine_.timeout.connect(self.update)
        self.engine_.start(16)

        for i, flag in enumerate(self.flags):
            value= QLabel(flag, self)
            value.adjustSize()

            value.move(i * 80, 20)

            self.belt_.append(value)

            self.show()



        












  