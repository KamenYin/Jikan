import sys
import pyautogui
from alarm import Alarm
from jikan import Clock, Pomodoro
from watches import Timer, StopWatch
from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QLocale, QTranslator
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QFrame,
    QGraphicsOpacityEffect
)





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

      

        # define basic layout of the window and set a custom size based on the dimensions of the system
        self.screenwidth, self.screenheight = pyautogui.size()
        self.title_ = self.tr("ジカン")
        self.setWindowTitle(self.title_)
        self.setWindowIcon(QIcon(QPixmap("taima_icons/時間.png")))
        self.setMinimumSize(QSize(self.screenwidth//2.5, self.screenheight // 2))
        self.layout_ = QVBoxLayout() # switched to Vertical to arrange the widgets more evenly. The idea being to place the native buttons in a frame on the top with the Widget housing the timer/stopwatch on the button 
        self.alarm_icon = QIcon(QPixmap("taima_icons/alarm_icon.png"))
        self.pod_icon = QIcon(QPixmap("taima_icons/pomo_icon.png"))
        self.timer_icon = QIcon(QPixmap("taima_icons/timer_icon.png"))
        self.stopwatch_icon = QIcon(QPixmap("taima_icons/stopwatch_icon.png"))
        self.light_icon = QIcon(QPixmap("taima_icons/light_mode_icon.png"))
        self.dark_icon = QIcon(QPixmap("taima_icons/dark_mode_icon.png"))
        self.border_col = ""



        self.light_dark_toggle_btn = QPushButton()
        self.mode_toggle_btn = QPushButton() # Intended to allow the user to change modes i.e. timer/stopwatch etc....

        self.light_dark_toggle_btn.setIcon(self.light_icon)
        self.mode_toggle_btn.setIcon(self.stopwatch_icon)


        self.native_frame = QFrame()  # frame to house the mode and light/dark toggles
        self.stack_manager = QStackedWidget() # frame responsible for housing/rendering the different modes
        self.timer_ = Timer()
        self.stopwatch_ = StopWatch()
        self.global_clock_ = Clock()
        self.pomodoro_ = Pomodoro()
        self.alarm_ = Alarm()
        
        self.light_dark_toggle_btn.setObjectName("native")
        self.mode_toggle_btn.setObjectName("native")
        self.icon_list = []
        
      
    
        #colors to be used
        self.darkamethyst = "#10002b"
        self.darkamethyst2= "#240046"
        self.indigoink= "#3c096c"
        self.indigovelvet= "#5a189a"
        self.royalviolet= "#7b2cbf"
        self.lavenderpurple= "#9d4edd"
        self.mauvemagic= "#c77dff"
        self.mauve= "#e0aaff"

       

       
        
      
       
        # default settings for light/dark mode 

        self.is_dark = True  # flag which controls/ indicates the current state
        self._bg_color = self.darkamethyst
        self.btn_bg_color = self.indigovelvet
        self.btn_font_color = self.mauvemagic
        self.display_font_color = self.mauve
        self.btn_hover = self.lavenderpurple
        self.btn_txt_hover = self.indigoink
        self.btn_pressed = self.indigoink
        self.txt_pressed = self.lavenderpurple
        self.btm_border = self.indigovelvet
        self.btm_border_focus = self.mauvemagic 
        self.spin_bg = 'transparent'

       

        self.native_frame.setFrameStyle(QFrame.Shape.Box)
        self.native_frame.setLineWidth(2.5)

        self.native_frame.setObjectName("native_box")

        self.frame_layout = QGridLayout()

        self.frame_layout.addWidget(self.mode_toggle_btn, 0,0)
        self.frame_layout.addWidget(self.light_dark_toggle_btn, 0,2)
        self.frame_layout.addWidget(self.global_clock_,0,1)

        self.native_frame.setLayout(self.frame_layout)
        self.stack_manager.addWidget(self.timer_)
        self.stack_manager.addWidget(self.stopwatch_)
        self.stack_manager.addWidget(self.pomodoro_)
        self.stack_manager.addWidget(self.alarm_)
    
        self.layout_.addWidget(self.native_frame)
        self.layout_.addWidget(self.stack_manager)
      
        self.light_dark_toggle_btn.setFixedSize(QSize(100,80))
        self.mode_toggle_btn.setFixedSize(QSize(100,80))

        # connecting the signals

        self.light_dark_toggle_btn.clicked.connect(self.set_light_dark)
        self.mode_toggle_btn.clicked.connect(self.toggle_modes)
        self.alarm_.alarm_signal.connect(self.render_alarm_popup)
        self.alarm_.snooze_signal.connect(self.render_snooze_popup)

               

        # set the layout in a central widget to be rendered in the main window
        self.widget = QWidget()
        self.widget.setLayout(self.layout_)
        self.setCentralWidget(self.widget)
        self.set_design()
        self.remove_shadow()
       

    
    def toggle_modes(self):
        self.icon_list = [self.timer_icon, self.stopwatch_icon, self.pod_icon, self.alarm_icon]
        if self.stack_manager.currentIndex() == 0:
            self.mode_toggle_btn.setIcon(self.icon_list[1])
            self.stack_manager.setCurrentIndex(1)
        
        elif self.stack_manager.currentIndex() == 1:
            self.mode_toggle_btn.setIcon(self.icon_list[2])
            self.stack_manager.setCurrentIndex(2)

        elif self.stack_manager.currentIndex() == 2:
            self.mode_toggle_btn.setIcon(self.icon_list[3])
            self.stack_manager.setCurrentIndex(3)

        else:
            self.mode_toggle_btn.setIcon(self.icon_list[0])
            self.stack_manager.setCurrentIndex(0)

    

    def render_alarm_popup(self, ring):
        if self.stack_manager.currentIndex() != 3 and ring:
            self.alarm_.handle_alarm_popup()


    def render_snooze_popup(self, snz):
         if self.stack_manager.currentIndex() != 3 and snz:
             self.alarm_.handle_snooze_popup()




    def remove_shadow(self):
        for child in self.findChildren(QPushButton):
            child.setDefault(False)
            child.setAutoDefault(False)
    
    def set_light_dark(self):
        self.is_dark = not self.is_dark
        if not self.is_dark:
            self._bg_color = self.mauvemagic
            self.btn_bg_color = self.darkamethyst2
            self.btn_font_color = self.mauvemagic
            self.display_font_color = self.indigoink
            self.btn_hover = self.indigovelvet
            self.btn_txt_hover = self.lavenderpurple            
            self.btn_pressed = self.indigoink
            self.txt_pressed = self.royalviolet
            self.cal_bg = self.darkamethyst2
            self.light_dark_toggle_btn.setIcon(self.dark_icon)
            self.btm_border =  "#290849"
            self.btm_border_focus = "#5F0BB2"
            self.spin_bg = self.darkamethyst2


        else:
            self._bg_color = self.darkamethyst
            self.btn_bg_color = self.indigovelvet
            self.btn_font_color = self.mauvemagic
            self.display_font_color = self.mauve
            self.btn_hover = self.lavenderpurple
            self.btn_txt_hover = self.indigoink
            self.btn_pressed = self.indigoink
            self.txt_pressed = self.lavenderpurple
            self.light_dark_toggle_btn.setIcon(self.light_icon)
            self.btm_border = self.indigovelvet
            self.btm_border_focus = self.mauvemagic
            self.spin_bg = 'transparent'
            

        #need to figure out how to tap into the QFrame's border
        self.border_col = self.darkamethyst if not self.is_dark else self.mauvemagic
        self.set_design()


    def handle_translator(self):
        pass

    
        
    def set_design(self):
        style =  f"""
            QWidget {{
             background: {self._bg_color}

             
            }}


            QFrame#native_box {{
                border-color: {self.border_col};
                border-radius: 25px;

            }}
            
            
            QPushButton {{

            border:2px solid transparent;
            color:{self.btn_font_color};
            width: 80px;
            height: 80px;
            border-radius: 50%;
            padding: 10px;
            font-family:'Revalia';
            font-size: 20px;
            background-color: {self.btn_bg_color};
            qproperty-iconSize: 40px 40px;
            
            }}


            QPushButton:hover {{
            background-color: {self.btn_hover};
            width:85px;
            font-size:24px;
            color: {self.btn_txt_hover};
            border:2px solid {self.btn_hover};



            }}

            QPushButton:focus {{
                outline: none;
                
            }}
            QPushButton:pressed {{
             
             border:1px solid {self.btn_pressed};
             background-color: {self.btn_pressed};
             color:{self.txt_pressed};
             width:40px;
             height:40px;
             outline:none;
             
            
             
            }}

          
            QPushButton#min_toggle {{
            margin:0px;
            border-radius:20%;
            qproperty-iconSize: 20px 20px;
           }}


            QLineEdit {{
              
              border: None;
              font-family: 'Rampart One';
              font-size: 100px;
              selection-background-color: transparent;
              selection-color: {self.display_font_color};
              color:{self.display_font_color};
              outline:none;
            }}


            QLineEdit:focus{{
                outline:none;
            }}


            QLabel#stopwatch_display{{
                font-size:80px;
            }}


            QLabel {{
                font-family: 'Rampart One';
                font-size: 80px;
                color:{self.display_font_color};
               
            }}


            QLabel#date_ {{
                font-family: 'Revalia';
                font-size: 15px;
              
                
            }}

             QLabel#time_ {{
                font-family: 'Revalia';
                font-size: 30px;
               
            }}

             QPushButton#native {{
                border-radius: 20px;

            }}

              QPushButton#pomo_btn {{
                border-radius: 20px;

            }}

             QLabel#pomo_sess_display {{
                font-size: 40px;
             

            }}

             QLabel#pomo_indi {{
                font-size: 25px;
                margin: 0px;
                padding:0px;
                border:none;
             

            }}

            QLabel#flag_display {{
                font-family: 'Revalia';
                font-size: 15px;
                margin: 0px;
                padding:10px;
                border:none;

             

                }}


            /*Edit Menu Styles*/

            QLabel#pomo_instructions {{
              font-family:'Revalia';
              font-size:14px;
              margin: 10px 0px 10px 0px;
              font-weight:bold;
            }}


            QLabel#pomo_warning {{
                font-family:'Revalia';
                font-size: 12px;
                color:'#e3669c';
                font-weight: normal;
            
            }}

            QPushButton#submit_btn{{
              
                border-radius:15px;

            }}

            QLabel#alarm_notif {{
             font-family: Revalia;
             font-size: 14px;
             font-weight: normal;

            }}



            QDateEdit {{
                font-family: 'Revalia';
                font-size: 23px;
                font-weight:bold;
                selection-background-color: transparent;
                selection-color: {self.display_font_color};
                color:{self.display_font_color};
                border:none;
                padding-right:10px;
                margin-right:10px;
            
            }}


            QTimeEdit {{
                
                font-family: 'Revalia';
                font-size: 50px;
                selection-background-color: transparent;
                selection-color: {self.display_font_color};
                color:{self.display_font_color};
                border:none;

            }}


         

           
            QTimeEdit::up-button, QTimeEdit::down-button {{
                width:40px;
                border: 2px solid transparent;
                border-style:outset;
                border-radius:10px;
                background:{self.btn_bg_color};
               
            }}



            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
                border-style: inset;
                border:2px solid {self.btn_pressed};
                background: {self.btn_pressed};
              
            }}

           

            QTimeEdit::up-button:pressed QTimeEdit::up-arrow, QTimeEdit::down-button:pressed QTimeEdit::down-arrow {{
                top:  1px;
                left: 1px;
            }}

            QTimeEdit::up-arrow {{
                image: url(taima_icons/up_icon.png);
                width: 35px;
                height:35px;
            }}

            QTimeEdit::down-arrow {{
                image: url(taima_icons/down_icon.png);
                width: 35px;
                height:35px;
            }}



        


            QPushButton#alarm_inner_btn {{
                border-radius: 20px;

            
                
            
            }}

            QPushButton#alarm_outer_btn {{
                border-radius: 50%;
            
            }}

            
         

        QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width:20px;
            border-left: 1px solid transparent;
            background-color: {self.btn_bg_color};
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}

        QDateEdit::drop-down:hover {{
            background-color: {self.btn_hover};
        }}

        QDateEdit::down-arrow {{
            image: url(taima_icons/down_icon.png);
            width: 30px;
            height: 30px;
        }}

        QDateEdit::drop-down:pressed {{
            background-color: {self.btn_pressed};
        }}

     

        /* Calendar Main Background */
        QCalendarWidget QWidget{{
            background-color: {self._bg_color};
            color: {self.display_font_color};
            font-family: 'Revalia';
            font-weight: normal;
        
        }}       

        QCalendarWidget QToolButton {{
            background-color: transparent;
            color: {self.btn_font_color};
            border-radius: 5px;       
            margin: 5px;
            padding: 10px;
            
            
           
        }}
        QCalendarWidget QToolButton#qt_calendar_prevmonth{{
            background-color:{self.btn_bg_color};

        }}

        QCalendarWidget QToolButton#qt_calendar_nextmonth{{
            background-color:{self.btn_bg_color};
            
        }}

         QCalendarWidget QToolButton#qt_calendar_prevmonth:hover{{
            background-color:{self.btn_hover};

        }}

        QCalendarWidget QToolButton#qt_calendar_nextmonth:hover{{
            background-color:{self.btn_hover};
            
        }}


         QCalendarWidget QToolButton#qt_calendar_prevmonth:pressed{{
            background-color:{self.btn_pressed};

        }}

        QCalendarWidget QToolButton#qt_calendar_nextmonth:pressed{{
            background-color:{self.btn_pressed};
            
        }}


        QCalendarWidget QSpinBox#qt_calendar_yearedit {{
            selection-background-color: transparent;
            selection-color: {self.display_font_color};
            color:{self.display_font_color};
            outline:none;
         
        }}
     


         /* Navigation Bar (Month and Year selectors) */
        QCalendarWidget QWidget#qt_calendar_navigationbar{{
            background-color: transparent;
          
            
        
        }}


        /* Navigation Buttons (Prev/Next Month) */
        QCalendarWidget QToolButton {{
            background-color:{self._bg_color};
            color:{self.display_font_color};
        
        }}
        

        /* Individual Day Cells */
        QCalendarWidget QAbstractItemView:enabled {{
            background-color: {self._bg_color};
            selection-background-color: {self.btn_bg_color};
            selection-color: {self.btn_font_color};
         
        }}




     
        QCalendarWidget QAbstractItemView::item:hover {{
           background-color: {self.royalviolet};
           color:'#CBA0EF';
          
        }}


        QCalendarWidget QAbstractItemView::item:selected {{
           background-color: {self.royalviolet};
           color:'#FCF9FE';
        }}
        

       

        
        /* Disabled Days (Days from other months) */
        QCalendarWidget QAbstractItemView:disabled {{
        color:'#ebd4f8' ;
    }}

        /* Combined the styling of the labels and line_edits*/
        QLabel#alarm_label, QLabel#pomo_edit_label {{
        
            font-family: Revalia;
            font-size: 14px;
            font-weight:bold;
            
        }}


        QLineEdit#alarm_name_edit, QLineEdit#pomo_input_field {{
            font-family: Revalia;
            font-size: 13px;
            font-weight:normal;
            color: {self.display_font_color};
            background-color: transparent;
            border:none;
            border-bottom:2px solid {self.btm_border};
            border-radius:5px;
        

        }}      

        

        QLineEdit#alarm_name_edit:focus, QLineEdit#pomo_input_field:focus {{
            border-bottom:2px solid {self.btm_border_focus};
         }}
    

        QSpinBox#alarm_spin {{
            font-family: Revalia;
            font-size: 13px;
            padding-right: 30px;
            font-weight:normal;
            background-color: {self.spin_bg};
            border: 2px solid transparent;
            border-bottom:2px solid {self.btm_border};
            border-radius:5px;
            selection-background-color: transparent;
            selection-color: {self.mauvemagic};
            color:{self.display_font_color if self.is_dark else self.mauvemagic};
        }}



        QSpinBox#alarm_spin::up-button {{
            subcontrol-position: top right;
            width: 20px;
    
        }}

        QSpinBox#alarm_spin::down-button {{
            subcontrol-origin: padding;
            subcontrol-position: bottom right;
            width: 20px;

            
        }}

     


     


        
        QSpinBox#alarm_spin:focus {{
        
            background-color: {self.indigoink};
            color:{self.mauvemagic};
            border-bottom:2px solid {self.btm_border_focus};
            border-radius:5px;
            
        }}



        QSpinBox#alarm_spin:disabled {{
            background-color: '#565357';
            border-bottom:2px solid grey;
            border-radius:5px;
            color:grey;
          
            

        }}

        QLabel#alarm_label:disabled {{
            color:grey;
        }}


        QPushButton#dt_submit {{
          border-radius: 20px;

        }}


        QLabel#almpop_label {{
            font-family:'Revalia';
            font-size: 20px;

        }}


        QPushButton#add_tone_btn {{
        
            border-radius: 15px;
        
        }}

       
       
        

            """
        app.setStyleSheet(style)


    def closeEvent(self, event):
        QApplication.instance().closeAllWindows()
        event.accept()



    
class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(QSize(500, 500))
        self.label_ = QLabel()
        self.label_.setPixmap(QPixmap("taima_icons/時間.png"))
        self.label_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.label_)
        self.setLayout(self.layout_)
        self.setStyleSheet("QWidget {background-color:#10002b; border-radius:20px;}")

        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.5)
        self.setGraphicsEffect(self.opacity_effect)

        # Fade-in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()

    def fade_out(self, callback=None):
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(800)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)

        if callback:
            self.fade_out_anim.finished.connect(callback)

        self.fade_out_anim.start()

  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    locale = QLocale.system().uiLanguages()
    if 'ja' not in locale[0]:
        translator = QTranslator()
        trans = translator.load("translations_en.qm")

        if trans:
            app.installTranslator(translator)
    
    splash = SplashWindow()
    splash.show()
    window = MainWindow()
    
    def show_main():
        window.show()
        splash.fade_out(splash.close)

    QTimer.singleShot(4000, show_main)
    sys.exit(app.exec())