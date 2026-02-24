# -*- coding: utf-8 -*-
"""
PDF Link Remover for Android
أداة حذف الروابط من ملفات PDF للاندرويد
Built with Kivy
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
import pypdf
import os
import re
from threading import Thread
from pathlib import Path

# Set window size
Window.size = (900, 1200)

class PDFLinkRemoverApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_file = None
        self.output_dir = None
        self.title = "PDF Link Remover"
        
    def build(self):
        """Build the UI"""
        # Request permissions
        request_permissions([Permission.READ_EXTERNAL_STORAGE, 
                            Permission.WRITE_EXTERNAL_STORAGE])
        
        # Main container
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        main_layout.canvas.before.clear()
        
        # Title
        title_label = Label(
            text='PDF Link Remover\nأداة حذف الروابط من PDF',
            font_size='20sp',
            bold=True,
            size_hint_y=0.1,
            color=(0, 0.8, 1, 1)
        )
        main_layout.add_widget(title_label)
        
        # File selection section
        file_frame = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        
        file_label = Label(
            text='اختر ملف PDF:',
            font_size='16sp',
            size_hint_y=0.3,
            bold=True,
            color=(0, 0.8, 1, 1)
        )
        file_frame.add_widget(file_label)
        
        self.file_display = Label(
            text='لم يتم اختيار ملف',
            font_size='12sp',
            size_hint_y=0.4
        )
        file_frame.add_widget(self.file_display)
        
        browse_btn = Button(
            text='استعرض الملفات',
            size_hint_y=0.3,
            background_color=(0, 0.8, 1, 1)
        )
        browse_btn.bind(on_press=self.show_file_chooser)
        file_frame.add_widget(browse_btn)
        
        main_layout.add_widget(file_frame)
        
        # Progress bar
        progress_label = Label(
            text='التقدم:',
            font_size='14sp',
            size_hint_y=0.05,
            bold=True
        )
        main_layout.add_widget(progress_label)
        
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=0.05
        )
        main_layout.add_widget(self.progress_bar)
        
        self.progress_text = Label(
            text='جاهز',
            font_size='12sp',
            size_hint_y=0.05
        )
        main_layout.add_widget(self.progress_text)
        
        # Log area
        log_label = Label(
            text='السجل:',
            font_size='14sp',
            size_hint_y=0.05,
            bold=True
        )
        main_layout.add_widget(log_label)
        
        scroll_view = ScrollView(size_hint_y=0.4)
        self.log_text = Label(
            text='جاهز للاستخدام...',
            font_size='10sp',
            markup=True,
            size_hint_y=None
        )
        self.log_text.bind(texture_size=self.log_text.setter('size'))
        scroll_view.add_widget(self.log_text)
        main_layout.add_widget(scroll_view)
        
        # Action buttons
        button_layout = GridLayout(cols=2, size_hint_y=0.15, spacing=5)
        
        process_btn = Button(
            text='حذف الروابط',
            background_color=(0, 1, 0, 1)
        )
        process_btn.bind(on_press=self.process_file)
        button_layout.add_widget(process_btn)
        
        reset_btn = Button(
            text='إعادة تعيين',
            background_color=(1, 0.7, 0, 1)
        )
        reset_btn.bind(on_press=self.reset)
        button_layout.add_widget(reset_btn)
        
        main_layout.add_widget(button_layout)
        
        return main_layout
    
    def show_file_chooser(self, instance):
        """Show file chooser popup"""
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserListView(
            filters=['*.pdf']
        )
        content.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        select_btn = Button(text='اختر')
        cancel_btn = Button(text='إلغاء')
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='اختر ملف PDF',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(instance):
            if file_chooser.selection:
                self.selected_file = file_chooser.selection[0]
                self.file_display.text = f'✓ {os.path.basename(self.selected_file)}'
                self.output_dir = os.path.dirname(self.selected_file)
                self.log('✓ تم اختيار الملف')
                popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def log(self, message):
        """Add to log"""
        self.log_text.text += f'\n• {message}'
    
    def remove_links(self, input_pdf, output_pdf):
        """Remove all links from PDF"""
        try:
            reader = pypdf.PdfReader(input_pdf)
            writer = pypdf.PdfWriter()
            
            total_pages = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages):
                # Update progress
                progress = int((page_num / total_pages) * 100)
                self.progress_bar.value = progress
                self.progress_text.text = f'معالجة الصفحة {page_num + 1} من {total_pages}'
                
                # Remove annotations
                if "/Annots" in page:
                    del page["/Annots"]
                if "/AA" in page:
                    del page["/AA"]
                if "/OpenAction" in page:
                    del page["/OpenAction"]
                if "/AcroForm" in page:
                    del page["/AcroForm"]
                
                # Remove links from content stream
                if "/Contents" in page:
                    try:
                        content = page["/Contents"]
                        if content:
                            if isinstance(content, list):
                                for obj in content:
                                    if hasattr(obj, 'get_object'):
                                        stream_data = obj.get_object().get_data()
                                        stream_data = self.remove_link_objects(stream_data)
                                        obj.get_object().set_data(stream_data)
                            else:
                                stream_data = content.get_object().get_data()
                                stream_data = self.remove_link_objects(stream_data)
                                content.get_object().set_data(stream_data)
                    except:
                        pass
                
                writer.add_page(page)
            
            # Remove document actions
            root = writer._root_object
            if "/OpenAction" in root:
                del root["/OpenAction"]
            if "/AA" in root:
                del root["/AA"]
            
            with open(output_pdf, "wb") as f:
                writer.write(f)
            
            self.progress_bar.value = 100
            self.progress_text.text = '✓ مكتمل!'
            self.log(f'✓ تمت المعالجة بنجاح')
            self.log(f'✓ الملف الجديد: {output_pdf}')
            
        except Exception as e:
            self.log(f'✗ خطأ: {str(e)}')
    
    def remove_link_objects(self, stream_data):
        """Remove link objects from stream"""
        try:
            text = stream_data.decode('latin-1', errors='ignore')
        except:
            text = str(stream_data)
        
        patterns = [
            r'/URI\s*\([^)]*\)',
            r'/A\s*<<[^>]*>>',
            r'/GoTo[^/]*',
            r't\.me[^\s>]*',
            r't\.com[^\s>]*',
            r'http[^\s>]*',
            r'https[^\s>]*',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        try:
            return text.encode('latin-1', errors='ignore')
        except:
            return stream_data
    
    def process_file(self, instance):
        """Process the selected file"""
        if not self.selected_file:
            self.log('✗ اختر ملف أولاً!')
            return
        
        output_file = os.path.join(
            self.output_dir,
            'no_links_' + os.path.basename(self.selected_file)
        )
        
        self.log('⏳ جاري معالجة الملف...')
        
        thread = Thread(target=self.remove_links, args=(self.selected_file, output_file))
        thread.daemon = True
        thread.start()
    
    def reset(self, instance):
        """Reset the app"""
        self.selected_file = None
        self.file_display.text = 'لم يتم اختيار ملف'
        self.progress_bar.value = 0
        self.progress_text.text = 'جاهز'
        self.log_text.text = 'جاهز للاستخدام...'

if __name__ == '__main__':
    PDFLinkRemoverApp().run()
