import os
import re
import shutil
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit,
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem, QMessageBox, QProgressBar)
from PyQt5.QtGui import QColor, QIcon

class FileCopyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('IMAGE FINDER')

        # Configuración de la ventana
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Botón para seleccionar ruta de origen
        self.source_btn = QPushButton('Seleccionar carpeta de origen', self)
        self.source_btn.clicked.connect(self.select_source_folder)
        layout.addWidget(self.source_btn)

        # Botón para seleccionar ruta de destino
        self.dest_btn = QPushButton('Seleccionar carpeta de destino', self)
        self.dest_btn.clicked.connect(self.select_dest_folder)
        layout.addWidget(self.dest_btn)

        # Área para pegar lista de archivos (seriales)
        self.serials_input = QTextEdit(self)
        layout.addWidget(QLabel('Pegar lista de seriales:'))
        layout.addWidget(self.serials_input)

        # Botón para empezar la búsqueda y copia
        self.copy_btn = QPushButton('Iniciar búsqueda y copia', self)
        self.copy_btn.clicked.connect(self.start_copy)
        layout.addWidget(self.copy_btn)

        # Lista de resultados
        self.result_list = QListWidget(self)
        layout.addWidget(self.result_list)

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Marca de agua
        self.watermark_label = QLabel('Developed by:', self)
        self.watermark_label.setStyleSheet('color: black; opacity: 0.7; font-size: 12px;')  # Estilo de la marca de agua
        layout.addWidget(self.watermark_label)

        self.setLayout(layout)

        self.source_folder = ''
        self.dest_folder = ''
        self.match_limit = 10  # Límite de coincidencias para grandes cantidades de datos

    def select_source_folder(self):
        self.source_folder = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de origen')
        if self.source_folder:
            self.source_btn.setText(f'Origen: {self.source_folder}')

    def select_dest_folder(self):
        self.dest_folder = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de destino')
        if self.dest_folder:
            self.dest_btn.setText(f'Destino: {self.dest_folder}')

    def start_copy(self):
        serials = self.serials_input.toPlainText().splitlines()

        if not self.source_folder:
            self.show_error_message('Por favor selecciona una carpeta de origen.')
            return
        if not self.dest_folder:
            self.show_error_message('Por favor selecciona una carpeta de destino.')
            return
        if not serials:
            self.show_error_message('Por favor ingresa una lista de seriales para buscar.')
            return

        self.result_list.clear()
        total_serials = len(serials)
        self.progress_bar.setMaximum(total_serials)

        for idx, serial in enumerate(serials):
            serial = serial.strip()
            if serial:
                found_files = self.find_and_copy_files(serial)

                # Verificación de coincidencias (llevadas a cabo por el usuario)
                if len(found_files) > 6:
                    reply = QMessageBox.question(self, 'Confirmación', 
                        f'Se han encontrado {len(found_files)} coincidencias con "{serial}". ¿Estás seguro de que deseas continuar?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        second_reply = QMessageBox.question(self, 'Confirmación', 
                            '¿Estás seguro de que deseas copiar estos archivos? Esto podría llenar el disco.',
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if second_reply == QMessageBox.No:
                            continue
                    else:
                        continue

                self.handle_existing_files(found_files)

            # Actualizar barra de carga del programa
            self.progress_bar.setValue(idx + 1)

    def find_and_copy_files(self, serial):
        pattern = re.escape(serial)
        found_files = []
        match_count = 0

        for root, dirs, files in os.walk(self.source_folder):
            for file in files:
                if re.search(pattern, file):
                    found_files.append((root, file))
                    match_count += 1
                    if match_count >= self.match_limit:  # Límite de coincidencias
                        return found_files

        return found_files

    def handle_existing_files(self, found_files):
        existing_files = []
        for root, file in found_files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(self.dest_folder, file)

            if os.path.exists(dest_file):
                existing_files.append(file)  
                self.display_result(file, found=True, existing=True)  
            else:
                shutil.copy2(source_file, dest_file)
                self.display_result(file, True) 

        for file in existing_files:
            self.display_result(file, found=True, existing=True) 

    def display_result(self, file, found, existing=False):
        item = QListWidgetItem(file)
        if existing:
            item.setBackground(QColor('blue')) 
        elif found:
            item.setBackground(QColor('green'))  
        else:
            item.setBackground(QColor('orange'))  
        self.result_list.addItem(item)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Error')
        msg.setText(message)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication([])
    ex = FileCopyApp()
    ex.show()
    app.exec_()
