from distutils.debug import DEBUG
from kivymd.tools.hotreload.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.anchorlayout import AnchorLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from itertools import cycle
from kivy.clock import Clock


class Cycle:
    def __init__(self):
        self.cycle = cycle([
            Timer(25), Timer(5), 
            Timer(25), Timer(5), 
            Timer(25), Timer(30)
            ]) 

    def __iter__(self):
        return self
        
    def __next__(self):
        return next(self.cycle)

class Timer:
    def __init__(self, time):
        self.time = time * 60
        
    def decrementar(self):
        self.time -= 1
        return self.time
    
    def __str__(self):
        return "{:02d}:{:02d}".format(*divmod(self.time, 60))

class Pomodoro(AnchorLayout):
#   self._tempo = next(self.tempo)
    timer_string = StringProperty('25:00')
    running = BooleanProperty(False)
    cycle = Cycle()
    pomodoro_valor = NumericProperty(1)
    pomodoro_cor = ListProperty([0, 0, 0])
    pomodoro_tamanho = NumericProperty(10)
#   tempo = Cycle()
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._time = next(self.cycle)
        self.timer_string = str(self._time)
        self.valor = int(100 / self._time.time)


    def start(self):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.update, 1)
            Clock.schedule_interval(self.temp, 1)

    def stop(self):
        if self.running:
            self.running = False
    
    def restart(self):
        if self.running:
            self.running = False
            Clock.schedule_interval(self.resetar, 1)

    def click(self):
        if self.running:
            self.stop()
        else:
            self.start()
    
    
    def resetar(self, *args):
        self.cycle = cycle([Timer(1), Timer(2), Timer(3), Timer(4), Timer(5), Timer(6)])
        self._time = next(self.cycle)
        self.timer_string = str(self._time)
        return False

    def update(self, *args):
        if self.running == False:
            return False 
        else:
            self.time = self._time.decrementar()
            if self.time == 0:
                self.stop()
                self.ids["botao_iniciar"].icon = self.icone
                self.ids["botao_reiniciar"].disabled = True
                self._time = next(self.cycle)
        self.timer_string = str(self._time)
 

    def temp(self, *args):
        if self.valor < 100:
            self.valor += 1
            self.pomodoro_valor += 1
            print(self.valor)
        if self.valor == 100:
            self.pomodoro_valor = 0
            self.valor = 0

class HotReload(MDApp):
    KV_FILES = ['App/teste.kv']
    DEBUG = True
    Window.size = (375, 812)

    def build_app(self):
        return Builder.load_file('App/teste.kv')

        
HotReload().run()