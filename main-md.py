from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card.card import MDCard
from kivymd.uix.fitimage.fitimage import FitImage
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivymd.uix.label import MDLabel
from kivymd.uix.button.button import MDRaisedButton
from kivy.core.window import Window
import requests
import io


# localhost
SERVER = 'http://127.0.0.1:8000'

# Текст презентации для проекта
texf_for_hh = "Добрый день. Данное приложение создано в качестве проекта для портфолио, приложение позволяет загрузить список доступных расскзов и прочесть нелинейную историю, меняющую сюжет в зависимости от выбора пользователя. Публичная часть создана на базе Kivy, серверная на FastApi. Для старта необходимо кликнуть на три вертикальные точки в правом верхнем углу."

# Получение id пользователя, необходимо для тестировани
get_user = requests.get(f'{SERVER}/user/get_id', headers = {"token": "TestToken"})
user_id = get_user.json()

# Создает Image
def get_image(img_name: str = None, file_extension: str = 'jpg') -> Image:
    get_img = requests.get(f'{SERVER}/image', headers = {"token": "TestToken", "img-name": img_name})
    buf = io.BytesIO(get_img.content)
    cim = CoreImage(buf, ext = file_extension)
    return Image(texture = cim.texture)    


# ЭКРАН №1 - home_page
class MyScrHome(MDScreen):
    def __init__(self, **kw):
        super(MyScrHome, self).__init__(**kw)
        self.screen_name = 'home_page'
        self.box = MDBoxLayout(orientation = 'horizontal')
        self.image = FitImage(source = "komarov.png")
        self.text = MDLabel(text = texf_for_hh)
        self.box.add_widget(self.image)
        self.box.add_widget(self.text)
        self.add_widget(self.box)


# КНОПКА В ШАГЕ НОВЕЛЛЫ
class MyStepBtn(MDRaisedButton):
    def __init__(self, myapp: 'APP' = None, novell_id = None, next_step_id: int = None, *arg, **kw):
        super().__init__(*arg, **kw)
        self.myapp = myapp
        self.novell_id = novell_id
        self.next_step_id = next_step_id
        self.on_press = self.next_step

    def next_step(self):
        self.myapp.screenmanager.screen_novell.clear_widgets()

        result = requests.get(f'{SERVER}/{user_id}/novells/{self.novell_id}/{self.next_step_id}', headers = {"token": "TestToken"})
        # print(result)
        # print(result.json())

        if result.json()['is_finish']:
            self.myapp.screenmanager.screen_novell.add_widget(MDLabel(text = "Вы прошли новеллу до конца. Благодарю за внивание!"))
        else:
            next_step = MyStep(myid = result.json()['id'],
                                novell_id = result.json()['id_novell'],
                                step_img = result.json()['img'], 
                                step_text = result.json()['text'], 
                                variants = result.json()['variants'], 
                                myapp = self.myapp)
            
            self.myapp.screenmanager.screen_novell.add_widget(next_step)


# ШАГ НОВЕЛЛЫ
class MyStep(MDBoxLayout):
    def __init__(self, myid:int = None, novell_id: int = None, step_img: str = None, step_text: str = None, variants: list[dict] = None, myapp: 'APP' =  None, *arg, **kw):
        super(MyStep, self).__init__(*arg, **kw)
        self.orientation = 'vertical'
        self.myid = myid 
        self.novell_id = novell_id 
        self.myapp = myapp
        self.variants = variants    
#        self.step_img = Image(source = '001.png')
        self.image = get_image(step_img)
        self.step_text = MDLabel(text = step_text)
        self.button_group = MDBoxLayout(orientation = 'horizontal')
        self.make_button_group()
        self.add_widget(self.image)
        self.add_widget(self.step_text)
        self.add_widget(self.button_group)

    def make_button_group(self):
        for var in self.variants:
            button = MyStepBtn(myapp = self.myapp, 
                               next_step_id = var['step_id'], 
                               text = var['button_text'],
                               novell_id = self.novell_id)
            self.button_group.add_widget(button)


# КАРТОЧКА В СПИСКЕ НОВЕЛЛ
class MyCard(MDRaisedButton):
    def __init__(self, myapp: 'APP' = None, myid: int = None, mytitle: str = None, mydescription: str = None, myposter: str = None, mygenre: str = None, myprice: int = None, *arg, **kw):
        super(MyCard, self).__init__(*arg, **kw)
        self.myid = myid
        self.mytitle = mytitle
        self.mydescription = mydescription
        self.myposter = myposter
        self.mygenre = mygenre
        self.myprice = myprice
        self.text = f'{mytitle}, жанр: {mygenre}' 
        self.myapp = myapp   
    
    def on_press(self, *arg):
        self.myapp.screenmanager.screen_novell.clear_widgets()
        result = requests.get(f'{SERVER}/{user_id}/novells/{self.myid}/start', 
                              headers = {"token": "TestToken"})
        print(result)
        print(result.json())
          
        first_step = MyStep(myid = result.json()['id'],
                            novell_id = result.json()['id_novell'],
                            step_img = result.json()['img'], 
                            step_text = result.json()['text'], 
                            variants = result.json()['variants'], 
                            myapp = self.myapp)
        
        self.myapp.screenmanager.screen_novell.add_widget(first_step)

        # Переход на экран с новеллой
        self.myapp.select_novell_page()
        

# ЭКРАН №2 - list_page
class MyScrList(MDScreen):
    def __init__(self, **kw):
        super(MyScrList, self).__init__(**kw)
        self.screen_name = 'list_page'
        self.scroll_box = MDScrollView()
        self.intro_box = MDGridLayout(cols = 1, spacing = 20, size_hint_y = None)
        self.scroll_box.add_widget(self.intro_box)
        self.add_widget(self.scroll_box)
 
            
# ЭКРАН №3 - novell_page
class MyScrNovell(MDScreen):
    def __init__(self, **kw):
        super(MyScrNovell, self).__init__(**kw)

    
# МЕНЕДЖЕР ЭКРАНОВ
class MyScreenManager(MDScreenManager):
    def __init__(self, myapp: 'APP' = None, **kw):
        super(MyScreenManager, self).__init__(**kw)
        self.myapp = myapp

        self.screen_home = (MyScrHome(name = 'home_page'))
        self.add_widget(self.screen_home)

        self.screen_list = (MyScrList(name = 'list_page'))
        self.add_widget(self.screen_list)

        self.screen_novell = (MyScrNovell(name = 'novell_page'))
        self.add_widget(self.screen_novell)


# СОЗДАНИЕ ПРИЛОЖЕНИЯ
class MyApp(MDApp):
    def __init__(self, **kw):
        super(MyApp, self).__init__(**kw)

        # Основной контейнер      
        self.mainbox = MDBoxLayout(orientation = 'vertical')

        # Навигационная панель
        self.navbar = MDTopAppBar(title = 'Панель MDToolbar',
                               left_action_items = [['home', self.select_home_page]],
                               right_action_items = [['dots-vertical', self.select_list_page]])
 
        # Менеджер экранов      
        self.screenmanager = MyScreenManager(myapp = self)

        self.mainbox.add_widget(self.navbar)
        self.mainbox.add_widget(self.screenmanager)

    def select_home_page(self, *arg, **kw):
        '''Кнопка перехода на главный экран, на MyScrHome'''
        self.screenmanager.current = 'home_page'

    def select_list_page(self, *arg, **kw):
        '''Кнопка перехода на экран cо списком новелл, на MyScrList'''
        if self.screenmanager.current == 'list_page':
            pass
        else:
            self.screenmanager.screen_list.intro_box.clear_widgets()
            result = requests.get(f'{SERVER}/{user_id}/novells', headers = {"token": "TestToken"})
            print(result)
            print(result.json())
            for novell in result.json():
                self.screenmanager.screen_list.intro_box.add_widget(MyCard(myid = novell['id'], 
                                                                            mytitle = novell['title'], 
                                                                            mydescription = novell['description'], 
                                                                            myposter = novell['poster'], 
                                                                            mygenre = novell['genre'],
                                                                            myprice = novell['price'], 
                                                                            myapp = self))     
            self.screenmanager.current = 'list_page'

    def select_novell_page(self, *arg, **kw):
        '''Кнопка перехода на экран c Новеллой, на MyScrNovell'''
        self.screenmanager.current = 'novell_page'

    # Возврат основного контейнера
    def build(self) -> MDBoxLayout: 
        return self.mainbox


# ЗАПУСК ПРИЛОЖЕНИЯ
APP = MyApp()
APP.run()