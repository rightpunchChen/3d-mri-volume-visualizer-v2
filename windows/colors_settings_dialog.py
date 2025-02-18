from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QColorDialog
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
import copy

class ColorsSettingsDialog(QDialog):
    color_updated = Signal(dict)

    def __init__(self, colors, default_colors):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 650)

        self.layout = QVBoxLayout(self)

        self.default_colors = copy.deepcopy(default_colors)
        self.selected_colors = copy.deepcopy(colors)

        self.general_buttons = {}
        self.mask_buttons = {}
        self.pred_buttons = {}

        general_label = QLabel("General Colors")
        self.layout.addWidget(general_label)
        for key in ["BACKGROUND_COLORS", "BRAIN_COLORS"]:
            hlayout = QHBoxLayout()
            lbl = QLabel(key.replace("_", " ").title())
            hlayout.addWidget(lbl)
            btn = QPushButton()
            btn.setFixedSize(100, 30)
            color_hex = self.tuple_to_hex(self.selected_colors[key])
            btn.setStyleSheet(f"background-color: {color_hex}")
            btn.clicked.connect(lambda checked, k=key: self.choose_color(k))
            hlayout.addWidget(btn)
            self.layout.addLayout(hlayout)
            self.general_buttons[key] = btn

        mask_label = QLabel("Mask Colors")
        self.layout.addWidget(mask_label)
        for i in range(1, 6):
            hlayout = QHBoxLayout()
            lbl = QLabel(f"Mask {i}")
            hlayout.addWidget(lbl)
            btn = QPushButton()
            btn.setFixedSize(100, 30)
            color_hex = self.tuple_to_hex(self.selected_colors["MASK_COLORS"][i])
            btn.setStyleSheet(f"background-color: {color_hex}")
            btn.clicked.connect(lambda checked, idx=i: self.choose_color("MASK_COLORS", idx))
            hlayout.addWidget(btn)
            self.layout.addLayout(hlayout)
            self.mask_buttons[i] = btn

        pred_label = QLabel("Prediction Colors")
        self.layout.addWidget(pred_label)
        for key in ['tp', 'fp', 'fn']:
            hlayout = QHBoxLayout()
            lbl = QLabel(key.upper())
            hlayout.addWidget(lbl)
            btn = QPushButton()
            btn.setFixedSize(100, 30)
            color_hex = self.tuple_to_hex(self.selected_colors["PRED_COLORS"][key])
            btn.setStyleSheet(f"background-color: {color_hex}")
            btn.clicked.connect(lambda checked, k=key: self.choose_color("PRED_COLORS", k))
            hlayout.addWidget(btn)
            self.layout.addLayout(hlayout)
            self.pred_buttons[key] = btn

        btn_layout = QHBoxLayout()

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.confirm)
        btn_layout.addWidget(self.confirm_button)

        self.reset_button = QPushButton("Default")
        self.reset_button.clicked.connect(self.reset_colors)
        btn_layout.addWidget(self.reset_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_button)

        self.layout.addLayout(btn_layout)

    def tuple_to_hex(self, t):
        r = int(t[0] * 255)
        g = int(t[1] * 255)
        b = int(t[2] * 255)
        return f"#{r:02X}{g:02X}{b:02X}"

    def tuple_to_qcolor(self, t):
        r = int(t[0] * 255)
        g = int(t[1] * 255)
        b = int(t[2] * 255)
        return QColor(r, g, b)

    def choose_color(self, category, subkey=None):
        if subkey is None:
            current_tuple = self.selected_colors[category]
            current_color = self.tuple_to_qcolor(current_tuple)
            color = QColorDialog.getColor(current_color, self)
            if color.isValid():
                new_tuple = (color.redF(), color.greenF(), color.blueF())
                self.selected_colors[category] = new_tuple
                btn = self.general_buttons[category]
                btn.setStyleSheet(f"background-color: {color.name()}")
        else:
            current_tuple = self.selected_colors[category][subkey]
            current_color = self.tuple_to_qcolor(current_tuple)
            color = QColorDialog.getColor(current_color, self)
            if color.isValid():
                new_tuple = (color.redF(), color.greenF(), color.blueF())
                self.selected_colors[category][subkey] = new_tuple
                if category == "MASK_COLORS":
                    btn = self.mask_buttons[subkey]
                else:
                    btn = self.pred_buttons[subkey]
                btn.setStyleSheet(f"background-color: {color.name()}")

    def reset_colors(self):
        self.selected_colors = copy.deepcopy(self.default_colors)

        for key, btn in self.general_buttons.items():
            color_hex = self.tuple_to_hex(self.selected_colors[key])
            btn.setStyleSheet(f"background-color: {color_hex}")

        for i, btn in self.mask_buttons.items():
            color_hex = self.tuple_to_hex(self.selected_colors["MASK_COLORS"][i])
            btn.setStyleSheet(f"background-color: {color_hex}")

        for key, btn in self.pred_buttons.items():
            color_hex = self.tuple_to_hex(self.selected_colors["PRED_COLORS"][key])
            btn.setStyleSheet(f"background-color: {color_hex}")

    def confirm(self):
        self.color_updated.emit(self.selected_colors)
        self.close()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dlg = ColorsSettingsDialog()

    dlg.color_updated.connect(lambda colors: print("New Colors:", colors))
    dlg.show()
    sys.exit(app.exec())
