# Main App to use pyinstaller
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Dir.Main import Ui_Main
from Dir.LoginWidget import LoginWidget

def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        login = LoginWidget()
        if login.exec_() == login.Accepted:
            user = getattr(login, 'user', None)
            Main = QMainWindow()
            ui = Ui_Main()
            ui.setupUi(Main, user=user)
            Main.show()
            sys.exit(app.exec_())
        else:
            sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n--- Error Occured {e}---\n")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

# BU GECEEEEE
    """
    soz derken kelime manasinda mi diyorsun anlamadim
    uykum var
    cok salak hissediyorum
        -Dasha
    """