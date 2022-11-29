import pyodbc
import pandas as pd
from itertools import cycle
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton
from kivymd.tools.hotreload.app import MDApp
from kivymd.uix.anchorlayout import AnchorLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivymd.uix.behaviors.backgroundcolor_behavior import BackgroundColorBehavior


#Funções do Pomodoro
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

class Pomodoro(MDFloatLayout):
    timer_string = StringProperty()
    running = BooleanProperty(False)
    icone = StringProperty('play-circle')
    cycle = Cycle()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._time = next(self.cycle)
        self.timer_string = str(self._time)

    def start(self):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.update, 1)

    def stop(self):
        if self.running:
            self.running = False
            Clock.schedule_interval(self.update, 1)

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
        self.cycle = cycle([Timer(25), Timer(5), Timer(25), Timer(5), Timer(25), Timer(30)])
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
    
class PomodoroAnimacao(AnchorLayout):
    pomodoro_cor = ListProperty([0, 0, 0])
    pomodoro_tamanho = NumericProperty(12)
    pomodoro_valor = NumericProperty(100)


#Função do Cadastrar/Login
dados_conexao = (
    "Driver={SQL Server};"
    "Server=DESKTOP-PQL2UTU\MSSQLSERVER01;"
    #"Server=localhost;"
    #"username=sa;"
    #"password=123456;"
    "Database=inTime;"
)
conexao = pyodbc.connect(dados_conexao)
cursor = conexao.cursor()


class Tela_Inicial(Screen, BackgroundColorBehavior):
    pass

class Login(Screen, BackgroundColorBehavior):
       
    def close_alert(self, obj):
        self.alert.dismiss()
    def show_alert(self):
        close_btn = MDFlatButton(text='Ok', on_release=self.close_alert)
        self.alert = MDDialog( title="Aviso", text="Email ou Senha inválidos", buttons=[close_btn])
        self.alert.open()

    def change_screen(self, *kwargs):
        self.manager.current = 'tela_relatorios'

    def autentication(self):
        email = self.ids.campo_email_user.text
        senha = self.ids.campo_senha_user.text
        banco = []
        colunas = ['Id_user', 
                    'User_nome', 
                    'User_sobrenome',
                    'User_email',
                    'User_senha',
                    'User_dt_nascimento', 
                    'User_genero', 
                    'User_img']
        
        query = cursor.execute(
            f"""
            SELECT * FROM Usuario WHERE User_email='{email}' AND User_senha='{senha}'
            """
        )
        for resutl in query:
            resutl = list(resutl)
            banco.append(resutl)
        user = pd.DataFrame(banco, columns=colunas)

        if user.empty:
            self.show_alert()

        else:
            Clock.schedule_once(self.change_screen, 1)
           
class Cadastrar(Screen, BackgroundColorBehavior):
    genero = 'Null'
    termos = False

    def close_alert(self, obj):
        self.alert.dismiss()
    def show_alert(self):
        close_btn = MDFlatButton(text='Ok', on_release=self.close_alert)
        self.alert = MDDialog( title="Aviso", text="Faltam informações nos campos", buttons=[close_btn])
        self.alert.open()

    def check_male(self, checkbox, active):
        self.genero = "Masculino"
    def check_female(self, checkbox, active):
        self.genero = "Feminino"
    def check_term_user(self):
        if self.termos == False:
            self.termos = True
        else:
            self.termos = False
   
    def cadastro(self):
        nome = self.ids.campo_nome.text
        sobrenome = self.ids.campo_sobrenome.text
        
        data = self.ids.campo_data.text
        data = data.replace('/', '-')

        email = self.ids.campo_email.text
        senha = self.ids.campo_senha.text
        conf_senha = self.ids.campo_confirmar_senha.text
        
        if nome != '' and email != '' and senha != '' and conf_senha != '' and senha == conf_senha and self.termos:
            query = cursor.execute(f"""SELECT COUNT(Id_user) from Usuario;""")
            
            for linhas in query:
                linhas = int(''.join(map(str, linhas)))
            
            cursor.execute(
                f"""
                INSERT INTO Usuario 
                VALUES ({linhas+1}, '{nome}', '{sobrenome}', '{email}', '{senha}', '{data}', '{self.genero}', Null);
                """
            )
            cursor.commit()
            nome = self.ids.campo_nome.text = ''
            sobrenome = self.ids.campo_sobrenome.text = ''           
            data = self.ids.campo_data.text = ''
            
            email = self.ids.campo_email.text = ''
            senha = self.ids.campo_senha.text = ''
            conf_senha = self.ids.campo_confirmar_senha.text = ''
        else:
             self.show_alert()

class Tela_Relatorios(Screen, BackgroundColorBehavior):
    pass

class Tela_Configuracoes(Screen, BackgroundColorBehavior):
    pass

class Tela_Configuracoes_Conta(Screen, BackgroundColorBehavior):
    pass

class Tela_Configuracoes_About(Screen, BackgroundColorBehavior):
    pass

class Tela_Tarefas(Screen, BackgroundColorBehavior):
    class Tarefa(MDCard):
        '''Implements a material design v3 card.'''
        titulo = StringProperty('Este aqui é um Título')
        data = StringProperty('20/11')
        text = StringProperty(
            'Exemplo aqui esta, para mostrar que deu tudo certo!!! Vamos continuar escrevendo algo só para ver ser ele aguenta colocar muito texto :3'
            )

    def botao_nova(self):
        self.add_widget(self.Tarefa(line_color=(0.2, 0.2, 0.2, 0.8), md_bg_color='#FFFFFF',))

class Tela_Lembretes(Screen, BackgroundColorBehavior):
    pass

class Tela_Temporizador(Screen, BackgroundColorBehavior):
    timer_string = StringProperty()
    running = BooleanProperty(False)
    icone = StringProperty('play-circle')
    cycle = Cycle()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._time = next(self.cycle)
        self.timer_string = str(self._time)

    def start(self):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.update, 1)

    def stop(self):
        if self.running:
            self.running = False
            Clock.schedule_interval(self.update, 1)

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
        self.cycle = cycle([Timer(25), Timer(5), Timer(25), Timer(5), Timer(25), Timer(30)])
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
    

class InTime(MDApp):
    Window.size = (375, 812)
    
    def build_app(self):
        return Builder.load_file('App/telas.kv')
