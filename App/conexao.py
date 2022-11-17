import pandas as pd
from kivymd.tools.hotreload.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import ObjectProperty
import pyodbc

dados_conexao = (
    "Driver={SQL Server};"
    "Server=DESKTOP-PQL2UTU\MSSQLSERVER01;"
    "Database=inTime;"
)
conexao = pyodbc.connect(dados_conexao)
cursor = conexao.cursor()


class Login(MDFloatLayout):
#    scr_mmgr_autentication = ObjectProperty(None)

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
            print("Autenticação Falhou")
            print("Senha ou Email inválidos")
        else:
            print("Autenticação Completa")
            

class Cadastrar(MDFloatLayout):
    pass

class Autenticar(MDApp):
    Window.size = (375, 812)

    def build_app(self, first=True):
        return Builder.load_file('App/telas_cadastro.kv')