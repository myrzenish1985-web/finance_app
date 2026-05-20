from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from database import Database

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Мои финансы', font_size='24sp', size_hint_y=0.1))
        
        btn_layout = GridLayout(cols=2, size_hint_y=0.4, spacing=10)
        
        btn_accounts = Button(text='💰 Счета')
        btn_accounts.bind(on_press=lambda x: setattr(self.manager, 'current', 'accounts'))
        
        btn_expenses = Button(text='📊 Расходы')
        btn_expenses.bind(on_press=lambda x: setattr(self.manager, 'current', 'expenses'))
        
        btn_transfers = Button(text='🔄 Переводы')
        btn_transfers.bind(on_press=lambda x: setattr(self.manager, 'current', 'transfers'))
        
        btn_reports = Button(text='📈 Отчеты')
        btn_reports.bind(on_press=lambda x: setattr(self.manager, 'current', 'reports'))
        
        btn_layout.add_widget(btn_accounts)
        btn_layout.add_widget(btn_expenses)
        btn_layout.add_widget(btn_transfers)
        btn_layout.add_widget(btn_reports)
        layout.add_widget(btn_layout)
        
        self.total_label = Label(text='', font_size='18sp', size_hint_y=0.1)
        layout.add_widget(self.total_label)
        
        self.plan_fact_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.plan_fact_layout.bind(minimum_height=self.plan_fact_layout.setter('height'))
        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(self.plan_fact_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.update_data()
    
    def update_data(self):
        total = self.db.get_total_balance()
        self.total_label.text = f'💰 Общий остаток: {total:,.2f} ₽'
        
        self.plan_fact_layout.clear_widgets()
        plan_fact = self.db.get_plan_vs_fact()
        
        for cat in plan_fact:
            name, planned, actual, remainder = cat
            status = '✅' if remainder >= 0 else '⚠️'
            label = Label(
                text=f'{name}: {status} План {planned:.0f} | Факт {actual:.0f} | Остаток {remainder:.0f}',
                size_hint_y=None,
                height=40
            )
            self.plan_fact_layout.add_widget(label)
    
    def on_enter(self):
        self.update_data()

class AccountsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        back_btn = Button(text='← На главную', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        layout.add_widget(Label(text='Доходные счета', font_size='20sp', size_hint_y=0.1))
        
        add_btn = Button(text='+ Добавить счет', size_hint_y=0.1)
        add_btn.bind(on_press=self.show_add_account_dialog)
        layout.add_widget(add_btn)
        
        self.accounts_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.accounts_layout.bind(minimum_height=self.accounts_layout.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.accounts_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_accounts()
    
    def load_accounts(self):
        self.accounts_layout.clear_widgets()
        accounts = self.db.get_accounts()
        
        for acc in accounts:
            acc_id, name, acc_type, balance, date = acc
            type_icon = '💳' if acc_type == 'current' else '🏦'
            
            box = BoxLayout(size_hint_y=None, height=60, spacing=5)
            box.add_widget(Label(text=f'{type_icon} {name}', size_hint_x=0.4))
            box.add_widget(Label(text=f'{balance:,.0f} ₽', size_hint_x=0.3))
            
            btn_del = Button(text='🗑', size_hint_x=0.15)
            btn_del.bind(on_press=lambda x, aid=acc_id: self.delete_account(aid))
            box.add_widget(btn_del)
            
            self.accounts_layout.add_widget(box)
    
    def show_add_account_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        name_input = TextInput(hint_text='Название счета', multiline=False)
        type_spinner = Spinner(text='Тип', values=['current', 'savings'])
        balance_input = TextInput(hint_text='Начальный баланс', text='0', input_filter='float')
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        btn_cancel = Button(text='Отмена')
        btn_save = Button(text='Сохранить')
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        
        content.add_widget(name_input)
        content.add_widget(type_spinner)
        content.add_widget(balance_input)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Новый счет', content=content, size_hint=(0.9, 0.5))
        
        def save(instance):
            if name_input.text:
                balance = float(balance_input.text) if balance_input.text else 0
                self.db.add_account(name_input.text, type_spinner.text, balance)
                self.load_accounts()
                popup.dismiss()
        
        btn_cancel.bind(on_press=popup.dismiss)
        btn_save.bind(on_press=save)
        popup.open()
    
    def delete_account(self, account_id):
        self.db.delete_account(account_id)
        self.load_accounts()
    
    def on_enter(self):
        self.load_accounts()

class ExpensesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        back_btn = Button(text='← На главную', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        layout.add_widget(Label(text='Статьи расходов', font_size='20sp', size_hint_y=0.1))
        
        add_btn = Button(text='+ Добавить статью', size_hint_y=0.1)
        add_btn.bind(on_press=self.show_add_category_dialog)
        layout.add_widget(add_btn)
        
        self.cats_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.cats_layout.bind(minimum_height=self.cats_layout.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.cats_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_categories()
    
    def load_categories(self):
        self.cats_layout.clear_widgets()
        categories = self.db.get_categories()
        
        for cat in categories:
            cat_id, name, acc_id, planned = cat
            actual = self.get_actual_sum(cat_id)
            remainder = planned - actual
            
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=2)
            
            top = BoxLayout(size_hint_y=0.5)
            top.add_widget(Label(text=name, font_size='14sp', halign='left'))
            
            btn_add_expense = Button(text='+ Расход', size_hint_x=0.2)
            btn_add_expense.bind(on_press=lambda x, cid=cat_id, cname=name: self.show_add_expense_dialog(cid, cname))
            top.add_widget(btn_add_expense)
            
            bottom = BoxLayout(size_hint_y=0.5)
            status = '✅' if remainder >= 0 else '⚠️'
            bottom.add_widget(Label(text=f'План: {planned:.0f} | Факт: {actual:.0f} | Остаток: {remainder:.0f} {status}'))
            
            box.add_widget(top)
            box.add_widget(bottom)
            self.cats_layout.add_widget(box)
    
    def get_actual_sum(self, category_id):
        self.db.cursor.execute('SELECT SUM(amount) FROM expenses WHERE category_id = ?', (category_id,))
        result = self.db.cursor.fetchone()[0]
        return result or 0
    
    def show_add_category_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        name_input = TextInput(hint_text='Название статьи', multiline=False)
        
        accounts = self.db.get_accounts()
        account_names = [f"{a[1]} ({a[2]})" for a in accounts]
        account_spinner = Spinner(text='Выберите счет', values=account_names)
        
        planned_input = TextInput(hint_text='Плановая сумма', text='0', input_filter='float')
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        btn_cancel = Button(text='Отмена')
        btn_save = Button(text='Сохранить')
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        
        content.add_widget(name_input)
        content.add_widget(account_spinner)
        content.add_widget(planned_input)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Новая статья', content=content, size_hint=(0.9, 0.5))
        
        def save(instance):
            if name_input.text and account_spinner.text != 'Выберите счет':
                selected = account_spinner.text
                for a in accounts:
                    if f"{a[1]} ({a[2]})" == selected:
                        acc_id = a[0]
                        break
                planned = float(planned_input.text) if planned_input.text else 0
                self.db.add_category(name_input.text, acc_id, planned)
                self.load_categories()
                popup.dismiss()
        
        btn_cancel.bind(on_press=popup.dismiss)
        btn_save.bind(on_press=save)
        popup.open()
    
    def show_add_expense_dialog(self, category_id, category_name):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text=f'Добавить расход: {category_name}'))
        
        amount_input = TextInput(hint_text='Сумма', input_filter='float', multiline=False)
        note_input = TextInput(hint_text='Примечание (опционально)', multiline=False)
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        btn_cancel = Button(text='Отмена')
        btn_save = Button(text='Добавить')
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        
        content.add_widget(amount_input)
        content.add_widget(note_input)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Новый расход', content=content, size_hint=(0.9, 0.4))
        
        def save(instance):
            if amount_input.text:
                amount = float(amount_input.text)
                self.db.add_expense(category_id, amount, note_input.text)
                self.load_categories()
                main_screen = self.manager.get_screen('main')
                main_screen.update_data()
                popup.dismiss()
        
        btn_cancel.bind(on_press=popup.dismiss)
        btn_save.bind(on_press=save)
        popup.open()
    
    def on_enter(self):
        self.load_categories()

class TransfersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        back_btn = Button(text='← На главную', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        layout.add_widget(Label(text='Переводы между счетами', font_size='20sp', size_hint_y=0.1))
        
        form = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=5)
        
        accounts = self.db.get_accounts()
        account_names = [a[1] for a in accounts]
        
        from_spinner = Spinner(text='Со счета', values=account_names)
        to_spinner = Spinner(text='На счет', values=account_names)
        amount_input = TextInput(hint_text='Сумма', input_filter='float', multiline=False)
        note_input = TextInput(hint_text='Примечание (опционально)', multiline=False)
        
        transfer_btn = Button(text='Выполнить перевод')
        transfer_btn.bind(on_press=lambda x: self.make_transfer(from_spinner, to_spinner, amount_input, note_input))
        
        form.add_widget(from_spinner)
        form.add_widget(to_spinner)
        form.add_widget(amount_input)
        form.add_widget(note_input)
        form.add_widget(transfer_btn)
        layout.add_widget(form)
        
        layout.add_widget(Label(text='История переводов', size_hint_y=0.05))
        self.history_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.history_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_history()
    
    def make_transfer(self, from_spinner, to_spinner, amount_input, note_input):
        if not amount_input.text:
            return
        if from_spinner.text == to_spinner.text:
            return
        
        accounts = self.db.get_accounts()
        from_id = None
        to_id = None
        
        for a in accounts:
            if a[1] == from_spinner.text:
                from_id = a[0]
            if a[1] == to_spinner.text:
                to_id = a[0]
        
        amount = float(amount_input.text)
        self.db.add_transfer(from_id, to_id, amount, note_input.text)
        amount_input.text = ''
        note_input.text = ''
        self.load_history()
        
        main_screen = self.manager.get_screen('main')
        main_screen.update_data()
    
    def load_history(self):
        self.history_layout.clear_widgets()
        transfers = self.db.get_transfers()
        
        for t in transfers:
            tid, from_name, to_name, amount, date, note = t
            text = f'{date}: {from_name} → {to_name} | {amount:.0f} ₽'
            if note:
                text += f' ({note})'
            label = Label(text=text, size_hint_y=None, height=35)
            self.history_layout.add_widget(label)
    
    def on_enter(self):
        self.load_history()

class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        back_btn = Button(text='← На главную', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        layout.add_widget(Label(text='Отчеты по расходам', font_size='20sp', size_hint_y=0.1))
        
        year_input = TextInput(hint_text='Год (например 2025)', text='2025', multiline=False, size_hint_y=0.1)
        btn_show = Button(text='Показать отчет', size_hint_y=0.1)
        
        self.report_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.report_layout.bind(minimum_height=self.report_layout.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.report_layout)
        
        layout.add_widget(year_input)
        layout.add_widget(btn_show)
        layout.add_widget(scroll)
        
        btn_show.bind(on_press=lambda x: self.show_report(year_input.text))
        
        self.add_widget(layout)
    
    def show_report(self, year_str):
        self.report_layout.clear_widgets()
        try:
            year = int(year_str)
            expenses = self.db.get_expenses_by_period(year)
            
            if not expenses:
                self.report_layout.add_widget(Label(text='Нет данных за этот год'))
                return
            
            for exp in expenses:
                label = Label(text=f'{exp[0]}: {exp[1]:,.0f} ₽', size_hint_y=None, height=35)
                self.report_layout.add_widget(label)
        except ValueError:
            self.report_layout.add_widget(Label(text='Введите корректный год'))

class FinanceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AccountsScreen(name='accounts'))
        sm.add_widget(ExpensesScreen(name='expenses'))
        sm.add_widget(TransfersScreen(name='transfers'))
        sm.add_widget(ReportsScreen(name='reports'))
        return sm

if __name__ == '__main__':
    FinanceApp().run()
