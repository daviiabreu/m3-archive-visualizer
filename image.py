# -*- coding: utf-8 -*-
import FreeSimpleGUI as sg
import cv2
import numpy as np

class ImageVisualizer:
    def __init__(self):
        sg.theme('DarkTeal9')
        self.window = sg.Window('Visualizador', self.layout(), resizable=True, finalize=True, size=(800,600))
        self.original_image = self.current_image = None
        self.history = []

    def layout(self):
        return [
            [sg.Button('Carregar', key='-LOAD-'), sg.Button('Salvar', key='-SAVE-'), sg.Button('Desfazer', key='-UNDO-'), sg.Button('Limpar', key='-CLEAR-')],
            [sg.Image(key='-ORIGINAL-'), sg.Image(key='-PROCESSED-')],
            [sg.Button('Cinza', key='-GRAY-'), sg.Button('Inverter Cores', key='-INV-'), sg.Button('Contraste', key='-CONTRAST-'), sg.Button('Nitidez', key='-SHARP-'), sg.Button('Bordas', key='-EDGE-'), sg.Button('Desfoque', key='-BLUR-')],
            [sg.Button('Rot90', key='-R90-'), sg.Button('Rot180', key='-R180-'), sg.Button('FlipH', key='-FH-'), sg.Button('FlipV', key='-FV-')],
            [sg.Text('Redimensionar'), sg.Slider((10,200),100,orientation='h',key='-RESIZE-'), sg.Button('Aplicar', key='-APPLY-')]
        ]

    def add_history(self, img):
        self.current_image = img
        self.history.append(img.copy())
        self.update_display()

    def update_display(self):
        if self.original_image is None or self.current_image is None: return
        def to_bytes(img): return cv2.imencode('.png', img)[1].tobytes()
        h = 300
        def resize(img):
            r = h/img.shape[0]
            return cv2.resize(img, (int(img.shape[1]*r), h))
        # Garantir RGB antes de exibir
        orig = self.original_image
        curr = self.current_image
        if len(orig.shape) == 3 and orig.shape[2] == 3:
            orig = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB) if np.mean(orig[:,:,0]) > np.mean(orig[:,:,2]) else orig
        if len(curr.shape) == 3 and curr.shape[2] == 3:
            curr = cv2.cvtColor(curr, cv2.COLOR_BGR2RGB) if np.mean(curr[:,:,0]) > np.mean(curr[:,:,2]) else curr
        self.window['-ORIGINAL-'].update(data=to_bytes(resize(orig)))
        self.window['-PROCESSED-'].update(data=to_bytes(resize(curr)))

    def run(self):
        while True:
            e,v = self.window.read(timeout=100)
            if e in (sg.WIN_CLOSED, 'Cancel'): break
            if e == '-LOAD-':
                f = sg.popup_get_file('Selecione', file_types=(('Imagens','*.png;*.jpg;*.jpeg;*.bmp;*.gif'),))
                if f:
                    try:
                        img_bgr = cv2.imread(f)
                        if img_bgr is None:
                            sg.popup_error('Arquivo inválido ou formato não suportado!')
                            continue
                        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                        self.original_image = self.current_image = img
                        self.history = [img.copy()]
                        self.update_display()
                    except Exception as ex:
                        sg.popup_error(f'Erro ao carregar imagem: {ex}')
            elif e == '-SAVE-':
                if self.current_image is not None:
                    f = sg.popup_get_file('Salvar como', save_as=True, default_extension='.png', file_types=(('PNG','*.png'),))
                    if f:
                        try:
                            cv2.imwrite(f, cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR))
                        except Exception as ex:
                            sg.popup_error(f'Erro ao salvar imagem: {ex}')
            elif e == '-UNDO-':
                if len(self.history)>1:
                    self.history.pop()
                    self.current_image = self.history[-1].copy()
                    self.update_display
                if self.current_image is not None:
                    self.add_history(cv2.bitwise_not(self.current_image))
            elif e == '-CONTRAST-':
                if self.current_image is not None:
                    lab = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2LAB)
                    l,a,b = cv2.split(lab)
                    cl = cv2.createCLAHE(3.0,(8,8)).apply(l)
                    img = cv2.cvtColor(cv2.merge((cl,a,b)), cv2.COLOR_LAB2RGB)
                    self.add_history(img)
            elif e == '-SHARP-':
                if self.current_image is not None:
                    k = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
                    self.add_history(cv2.filter2D(self.current_image,-1,k))
            elif e == '-EDGE-':
                if self.current_image is not None:
                    g = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2GRAY)
                    eimg = cv2.Canny(g,100,200)
                    self.add_history(cv2.cvtColor(eimg, cv2.COLOR_GRAY2RGB))
            elif e == '-BLUR-':
                if self.current_image is not None:
                    k = 11
                    self.add_history(cv2.GaussianBlur(self.current_image,(k,k),0))
            elif e == '-R90-':
                if self.current_image is not None:
                    self.add_history(cv2.rotate(self.current_image, cv2.ROTATE_90_CLOCKWISE))
            elif e == '-R180-':
                if self.current_image is not None:
                    self.add_history(cv2.rotate(self.current_image, cv2.ROTATE_180))
            elif e == '-FH-':
                if self.current_image is not None:
                    self.add_history(cv2.flip(self.current_image,1))
            elif e == '-FV-':
                if self.current_image is not None:
                    self.add_history(cv2.flip(self.current_image,0))
            elif e == '-APPLY-':
                if self.current_image is not None:
                    f = v['-RESIZE-']/100.0
                    w = int(self.current_image.shape[1]*f)
                    h = int(self.current_image.shape[0]*f)
                    self.add_history(cv2.resize(self.current_image,(w,h)))
        self.window.close()

if __name__ == '__main__':
    ImageVisualizer().run()