import pandas as pd
from kivymd.tools.hotreload.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.properties import ObjectProperty
import pyodbc

dados_conexao = (
    "Driver={SQL Server};"
    #"Server=DESKTOP-PQL2UTU\MSSQLSERVER01;"
    "Server=localhost;"
    "username=sa;"
    "password=123456;"
    "Database=inTime;"
)
conexao = pyodbc.connect(dados_conexao)
cursor = conexao.cursor()

class Login(MDFloatLayout):

    def close_alert(self, obj):
        self.alert.dismiss()
    def show_alert(self):
        close_btn = MDFlatButton(text='Ok', on_release=self.close_alert)
        self.alert = MDDialog( title="Aviso", text="Email ou Senha inválidos", buttons=[close_btn])
        self.alert.open()

    def autentication(self):
        email = self.ids.campo_email_user.text
        senha = self.ids.campo_senha_user.text
        banco = []
        colunas = ['Id_user', 'User_nome', 'User_sobrenome', 'User_email', 'User_senha', 'User_dt_nascimento', 'User_genero', 'User_img']
        
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
            print('Sucess')
            

class Cadastrar(MDFloatLayout):
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

class Autenticar(MDApp):
    Window.size = (375, 812)

    def build(self):
        return Builder.load_file("App/telas_cadastro.kv")