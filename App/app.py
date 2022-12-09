import os
import pyodbc
import locale
import unidecode
import webbrowser
import pandas as pd
from itertools import cycle
from kivy.clock import Clock
from kivy.lang import Builder
from datetime import datetime
from kivymd.uix.card import MDCard
from kivy.core.window import Window
from kivy.animation import Animation
from kivymd.uix.dialog import MDDialog
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.tools.hotreload.app import MDApp
from kivymd.uix.anchorlayout import AnchorLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
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


#Conexão com o Banco de Dados
dados_conexao = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=inTime-db.mssql.somee.com;"
    "UID=LPMS_SQLLogin_1;"
    "PWD=xjbdvem1hd;"
    "Database=inTime-db;"
    "TrustServerCertificate=yes;"
)
conexao = pyodbc.connect(dados_conexao)
cursor = conexao.cursor()
cursor1 = conexao.cursor()
cursor2 = conexao.cursor()
cursor3 = conexao.cursor()
cursor4 = conexao.cursor()
cursor5 = conexao.cursor()

#Telas do Aplicativo
class Tela_Inicial(Screen, BackgroundColorBehavior):
    def check_autentication(self):
        try:
            with open('App/log.txt', 'r') as d:
                linhas = d.readlines()
                if linhas == '':
                    self.manager.current = 'tela_entrar'
                else:
                    self.manager.transition.direction = 'left'
                    self.manager.current = 'tela_relatorios'
        except IOError:
            self.manager.current = 'tela_entrar'

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
        
        banco_usuario = []
        colunas_usuario = ['Id_user', 
                           'User_nome', 
                           'User_sobrenome',
                           'User_email',
                           'User_senha',
                           'User_dt_nascimento', 
                           'User_genero', 
                           'User_img']
        
        banco_tarefas = []
        colunas_tarefas = ['Id_tarefa',
                           'Tarefa_titulo',
                           'Tarefa_desc',
                           'Tarefa_prazo',
                           'Tarefa_status',
                           'Id_user']
        
        banco_lembretes = []
        colunas_lembretes = ['Id_lembrete',
                             'Lembrete_titulo',
                             'Lembrete_desc',
                             'Id_user']

        query = cursor1.execute(
            f"""
            SELECT * FROM Usuario WHERE User_email='{email}' AND User_senha='{senha}';
            """
        )
        #Loop para checar se Senha e Email estão corretos
        for result in query:
            result = list(result)
            banco.append(result)
        user = pd.DataFrame(banco, columns=colunas)
        
        if user.empty:
            self.show_alert()
     
        else:
            ids = int(user['Id_user'][0])
            tab_usuario = cursor2.execute(
                f"""
                SELECT * FROM Usuario WHERE User_email='{email}' AND User_senha='{senha}';
                """
            )
            for usuario in tab_usuario:
                usuario = list(usuario)
                banco_usuario.append(usuario)

            tab_tarefas = cursor3.execute(
                f"""
                SELECT * FROM Tarefas WHERE Id_user='{ids}';
                """
            )
            for tarefa in tab_tarefas:
                tarefa = list(tarefa)
                banco_tarefas.append(tarefa)

            tab_lembretes = cursor4.execute(
                f"""
                SELECT * FROM Lembretes WHERE Id_user='{ids}';
                """
            )
            for lembrete in tab_lembretes:
                lembrete = list(lembrete)
                banco_lembretes.append(lembrete)

            
            #Logs para escrever no arquivo
            log_usuario = pd.DataFrame(banco_usuario, columns=colunas_usuario)
            log_tarefas = pd.DataFrame(banco_tarefas, columns=colunas_tarefas)
            log_lembretes = pd.DataFrame(banco_lembretes, columns=colunas_lembretes)

            #Escrevendo dados no arquivo 'log.txt'
            with open('App/log.txt', 'w') as f:
                f.write(unidecode.unidecode(log_usuario.to_string(index=False)))
                f.write('\n')
                f.write('\n')
                f.write(unidecode.unidecode(log_tarefas.to_string(index=False)))
                f.write('\n')
                f.write('\n')
                f.write(unidecode.unidecode(log_lembretes.to_string(index=False)))
            
            #Mudando para as tela do usuário
            Clock.schedule_once(self.change_screen, 1)
           
class Cadastrar(Screen, BackgroundColorBehavior):
    genero = 'Null'
    termos = False

    def terms(self):
        webbrowser.open('https://lucasbunny.github.io/InTime_Site/assets/docs/InTime%20App%20-%20Política%20de%20Privacidade%20e%20Termos%20de%20Uso.pdf')

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
            
            self.manager.current = 'tela_entrar'
        else:
             self.show_alert()

class Tela_Relatorios(Screen, BackgroundColorBehavior):
    pass

class Tela_Configuracoes(Screen, BackgroundColorBehavior):
    def site(self):
        webbrowser.open('https://lucasbunny.github.io/InTime_Site')

class Tela_Configuracoes_Conta(Screen, BackgroundColorBehavior):
    def close_alert(self, obj):
        self.alert.dismiss()
    def show_alert(self, *kwargs):
        close_btn = MDFlatButton(text='Ok', on_release=self.close_alert)
        self.alert = MDDialog( title="Aviso", text="Preencha todos os campos e cheque se as informações estão corretas", buttons=[close_btn])
        self.alert.open()
    
    def excluir_log(self, *kwargs):
        os.remove('App/log.txt')
        self.manager.current = 'tela_inicial'
    
    def salvar_alteracao(self):
        novo_nome = self.ids.input_nome.text
        novo_sobrenome = self.ids.input_sobrenome.text
        email_novo = self.ids.input_email.text
        senha_nova = self.ids.input_nova_senha.text
        confirma_senha = self.ids.input_confirma_senha.text
        
        with open('App/log.txt', 'r') as b:
            b.readline()
            ids = b.readline()
        id = list(ids)
        id = id[7]

        if novo_nome != '' and novo_sobrenome != '' and email_novo != '' and senha_nova != '' and confirma_senha != '' and senha_nova == confirma_senha:
            cursor5.execute(
                f'''
                UPDATE Usuario SET User_nome='{novo_nome}', User_sobrenome='{novo_sobrenome}', User_email='{email_novo}', User_senha='{confirma_senha}'
                WHERE Id_user='{id}'
                ''')
            cursor5.commit()
            
            novo_nome = self.ids.input_nome.text = ''
            novo_sobrenome = self.ids.input_sobrenome.text = ''
            email_novo = self.ids.input_email.text = ''
            senha_nova = self.ids.input_nova_senha.text = ''
            confirma_senha = self.ids.input_confirma_senha.text = ''
            
            Clock.schedule_once(self.excluir_log, 1)
        else:
            Clock.schedule_once(self.show_alert, 1)

class Tela_Configuracoes_About(Screen, BackgroundColorBehavior):
    def terms(self):
        webbrowser.open('https://lucasbunny.github.io/InTime_Site/assets/docs/InTime%20App%20-%20Política%20de%20Privacidade%20e%20Termos%20de%20Uso.pdf')
    def site(self):
        webbrowser.open('https://lucasbunny.github.io/InTime_Site')

class Tela_Tarefas(Screen, BackgroundColorBehavior):
    class Tarefa(MDCard):
    
        titulo = StringProperty('')
        data = StringProperty('')
        text = StringProperty('')
        click = 1

        def close_alert(self, obj):
            self.alert.dismiss()
        def show_alert(self):
            close_btn = MDFlatButton(text='Ok', on_release=self.close_alert)
            self.alert = MDDialog( title="Aviso", text="Valores incorretos. Por favor insira os valores de maneira a respeitar os campos.", buttons=[close_btn])
            self.alert.open()

        def user_click_open(self):
            t = Tela_Tarefas()
            if self.click == 1:
                Animation(
                    size=(300, 300), 
                    duration=0.1,
                    t='in_quad',
                ).start(self)

                self.btn1 = MDRaisedButton(text='Excluir', pos_hint={'center_x':.1, 'center_y':.07}, size_hint=(.2, 0.06), on_release=lambda x:t.excluir()) 
                self.btn2 = MDRaisedButton(text='Salvar', pos_hint={'center_x':.47, 'center_y':.07}, size_hint=(.3, 0.06), on_release=lambda x:self.salvar()) 
                self.btn3 = MDRaisedButton(text='Finalizar Tarefa', pos_hint={'center_x':.9, 'center_y':.07}, size_hint=(.2, 0.06)) 
                self.btn4 = MDIconButton(icon='close', pos_hint={'center_x':.05, 'center_y':.96}, on_release=lambda x:self.user_click_close())

                self.label_title = MDTextField(text=self.titulo, hint_text='Título', size_hint=(.5, None), pos_hint={'center_x': .3, 'center_y': 0.85}, multiline=True, line_color_normal='white', line_color_focus="white", text_color_normal='black', text_color_focus='black', hint_text_color_focus="black",  max_text_length=15)
                self.label_text = MDTextField(text=self.text, hint_text='Breve descrição da Tarefa.', size_hint=(.9, None), pos_hint={'center_x': .51, 'center_y': .649}, multiline=True, line_color_normal='white', line_color_focus="white", text_color_normal='black', text_color_focus='black', hint_text_color_focus="black", max_text_length=84)
                self.label_data = MDTextField(text=self.data, hint_text='Conclusão', helper_text='yyyy/mm/dd', size_hint=(.3, None), pos_hint={'center_x': 0.83, 'center_y': 0.85}, validator="date", date_format="yyyy/mm/dd", line_color_normal='white', line_color_focus="white", text_color_normal='black', text_color_focus='black', hint_text_color_focus="black")
                
                self.titulo = ''
                self.text = ''
                self.data = ''

                self.ids.layout_tarf.add_widget(self.btn1)
                self.ids.layout_tarf.add_widget(self.btn2)
                self.ids.layout_tarf.add_widget(self.btn3)
                self.ids.layout_tarf.add_widget(self.btn4)

                self.ids.layout_tarf.add_widget(self.label_title)
                self.ids.layout_tarf.add_widget(self.label_text)
                self.ids.layout_tarf.add_widget(self.label_data)

                self.click = 2

        def user_click_close(self):
            if self.click == 2:
                Animation(
                    size=(300, 150), 
                    duration=0.1,
                    t='in_quad',
                ).start(self)
                
                self.ids.label_titulo.pos=(3, 45)
                self.ids.label_data.pos=(200, 45)
                self.ids.label_texto.pos=(3, -35)


                self.ids.layout_tarf.remove_widget(self.btn1)
                self.ids.layout_tarf.remove_widget(self.btn2)
                self.ids.layout_tarf.remove_widget(self.btn3)
                self.ids.layout_tarf.remove_widget(self.btn4)
                
                self.ids.layout_tarf.remove_widget(self.label_title)
                self.ids.layout_tarf.remove_widget(self.label_text)
                self.ids.layout_tarf.remove_widget(self.label_data)

                self.titulo = ''
                self.text = ''
                self.data = ''
                
                self.click = 1
        
        def salvar(self):
            if self.label_data.error or self.label_title.error or self.label_text.error:
                self.show_alert()
            else:
                if self.click == 2:
                    Animation(
                        size=(300, 150), 
                        duration=0.1,
                        t='in_quad',
                    ).start(self)
                    
                    self.ids.label_titulo.pos=(3, 45)
                    self.ids.label_data.pos=(200, 45)
                    self.ids.label_texto.pos=(3, -35)


                    self.ids.layout_tarf.remove_widget(self.btn1)
                    self.ids.layout_tarf.remove_widget(self.btn2)
                    self.ids.layout_tarf.remove_widget(self.btn3)
                    self.ids.layout_tarf.remove_widget(self.btn4)
                    
                    self.ids.layout_tarf.remove_widget(self.label_title)
                    self.ids.layout_tarf.remove_widget(self.label_text)
                    self.ids.layout_tarf.remove_widget(self.label_data)

                    self.titulo = self.label_title.text
                    self.text = self.label_text.text
                    self.data = self.label_data.text
                    
                    self.click = 1
   
    def excluir(self):
        self.ids.tarf.remove_widget(self.Tarefa)

    def botao_nova(self):
        self.ids.tarf.add_widget(self.Tarefa(line_color=(0.2, 0.2, 0.2, 0.8), md_bg_color='#FFFFFF',))

class Tela_Lembretes(Screen, BackgroundColorBehavior):
    class Lembrete(MDCard):
        titulo = StringProperty('')
        text = StringProperty('')
        click = 1
        
        def close_alert(self, obj):
            self.alert.dismiss()
        def show_alert(self):
            close_btn = MDFlatButton(text='Ok', on_release=self.close_alert)
            self.alert = MDDialog( title="Aviso", text="Valores incorretos. Por favor insira os valores de maneira a respeitar os campos.", buttons=[close_btn])
            self.alert.open()

        def click_open(self):
            t = Tela_Lembretes()
            if self.click == 1:
                Animation(
                    size=(300, 300), 
                    duration=0.1,
                    t='in_quad',
                ).start(self)

                self.btn1 = MDRaisedButton(text='Excluir', pos_hint={'center_x':.1, 'center_y':.07}, size_hint=(.2, 0.06), on_release=lambda x:t.excluir()) 
                self.btn2 = MDRaisedButton(text='Salvar', pos_hint={'center_x':.47, 'center_y':.07}, size_hint=(.3, 0.06), on_release=lambda x:self.salvar())  
                self.btn3 = MDIconButton(icon='close', pos_hint={'center_x':.05, 'center_y':.96}, on_release=lambda x:self.click_close())

                self.label_title = MDTextField(text=self.titulo, hint_text='Título', size_hint=(.9, None), pos_hint={'center_x': .51, 'center_y': 0.85}, multiline=True, line_color_normal='white', line_color_focus="white", text_color_normal='black', text_color_focus='black', hint_text_color_focus="black",  max_text_length=30)
                self.label_text = MDTextField(text=self.text, hint_text='Breve descrição da Tarefa.', size_hint=(.9, None), pos_hint={'center_x': .51, 'center_y': .649}, multiline=True, line_color_normal='white', line_color_focus="white", text_color_normal='black', text_color_focus='black', hint_text_color_focus="black", max_text_length=84)
                 
                self.titulo = ''
                self.text = ''

                self.ids.layout_lemb.add_widget(self.btn1)
                self.ids.layout_lemb.add_widget(self.btn2)
                self.ids.layout_lemb.add_widget(self.btn3)

                self.ids.layout_lemb.add_widget(self.label_title)
                self.ids.layout_lemb.add_widget(self.label_text)

                self.click = 2

        def click_close(self):
            if self.click == 2:
                Animation(
                    size=(300, 150), 
                    duration=0.1,
                    t='in_quad',
                ).start(self)
                
                self.ids.label_titulo.pos=(3, 45)
                self.ids.label_texto.pos=(3, -35)


                self.ids.layout_lemb.remove_widget(self.btn1)
                self.ids.layout_lemb.remove_widget(self.btn2)
                self.ids.layout_lemb.remove_widget(self.btn3)
                
                self.ids.layout_lemb.remove_widget(self.label_title)
                self.ids.layout_lemb.remove_widget(self.label_text)

                self.titulo = ''
                self.text = ''
                
                self.click = 1

        def salvar(self):
                if self.label_title.error or self.label_text.error:
                    self.show_alert()
                else:
                    if self.click == 2:
                        Animation(
                            size=(300, 150), 
                            duration=0.1,
                            t='in_quad',
                        ).start(self)
                        
                        self.ids.label_titulo.pos=(3, 45)
                        self.ids.label_texto.pos=(3, -35)


                        self.ids.layout_lemb.remove_widget(self.btn1)
                        self.ids.layout_lemb.remove_widget(self.btn2)
                        self.ids.layout_lemb.remove_widget(self.btn3)
                        
                        self.ids.layout_lemb.remove_widget(self.label_title)
                        self.ids.layout_lemb.remove_widget(self.label_text)

                        self.titulo = self.label_title.text
                        self.text = self.label_text.text
                        
                        self.click = 1

    def excluir(self):
        self.ids.lemb.remove_widget(self.Lembrete)

    def botao_nova(self):
        self.ids.lemb.add_widget(self.Lembrete(line_color=(0.2, 0.2, 0.2, 0.8), md_bg_color='#FFFFFF',))

class Tela_Temporizador(Screen, BackgroundColorBehavior):
    timer_string = StringProperty()
    running = BooleanProperty(False)
    icone = StringProperty('play-circle')
    cycle = Cycle()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._time = next(self.cycle)
        self.timer_string = str(self._time)
        self.sound = SoundLoader.load('Songs\Pixie Dust Android.mp3')

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
                self.sound.play()
        self.timer_string = str(self._time) 
    
class InTime(MDApp):
    Window.size = (375, 812)

    def build_app(self):
        return Builder.load_file('App/telas.kv')
    
    #Informações da Tela de Relatórios 
    info_horario = datetime.today().strftime('%X')
    locale.setlocale(locale.LC_TIME, 'pt_BR')
    info_data = datetime.today().strftime('%A, %d de %B de %Y')
    comprimentos = StringProperty('')
    info_nome = StringProperty('')
    def informations(self):
        try:
            with open('App/log.txt', 'r') as f:
                f.readline()
                linha = f.readline()
            nome = linha.split()
            self.info_nome = nome[1]
        except FileNotFoundError:
            pass
        self.comprimentos = self.info_periodo + ', ' + self.info_nome + '!'
    def periodo(hora):
        if '06:00:00' < hora < '11:59:00': return 'Bom Dia'
        elif '12:00:00' < hora < '17:59:00': return 'Boa Tarde'
        elif '18:00:00' < hora < '23:59:00': return 'Boa Noite'
        return ''
    info_periodo = periodo(info_horario) 