const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const path = require('path');
const deploy_env = process.env.DEPLOY_ENV;
let pyProc = null;
let pyPort = null;
let appath = app.getPath();
console.log("DIRNAME", __dirname);
console.log("APP PATH", appath);

let mainWindow = null
const createWindow = () => {
    mainWindow = new BrowserWindow({
        width: 950, height: 700,
        minWidth: 950, minHeight: 700,
        maxWidth: 950, maxHeight: 700,
        center: true, 
        frame: false,
        darkTheme: true,
        fullscreen: false,
        resizable: false,
        icon: path.join(__dirname, 'imgs/TridentFrame_Icon_200px.png'),
        webPreferences: {
            webSecurity: false,
            nodeIntegration: true,
        },
    });
    mainWindow.setMenu(null);
    if (deploy_env && deploy_env == "DEV") { // Development environment
        console.log("------ DEVELOPMENT VERSION ------");
        mainWindow.loadURL("http://localhost:8080/")
    }
    else {
        console.log("------ PRODUCTION VERSION ------");
        // Production environment
        mainWindow.loadURL(require('url').format({
            pathname: path.join(__dirname, './release/html/index.html'),
            protocol: 'file:',
            slashes: true
        }));
    }

    // if (deploy_env && deploy_env == 'DEV') {
        mainWindow.webContents.openDevTools({detach: true});
    // }
    mainWindow.focus();
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.on('ready', createWindow);
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin'){
        app.quit();
    }
})
app.on('activate', () => {
    if (mainWindow === null){
        createWindow();
    }
})

const selectPort = () => {
    pyPort = 4242;
    return pyPort;
}

const createPyProc = () => {
    let port = '' + selectPort();
    if (deploy_env && deploy_env == 'DEV') {
        let script = path.join(__dirname, 'main.py');
        pyProc = require('child_process').spawn('python', [script, port]);
        if (pyProc != null) {
          console.log('development child process success');
        }
    }
    else {
        let script = "";
        if (process.platform == 'win32') {
            script = path.join(__dirname, 'dist/tridentframe_win/main.exe');
        }
        else if (process.platform == 'linux') {
            script = path.join(__dirname, 'release/tridentframe_linux/main');
        }
        console.log(`Obtained python path script: \n${script}`);
        pyProc = require('child_process').spawn(script);
        if (pyProc != null) {
          console.log('production child process success');
        }
    }
}

const exitPyProc = () => {
    pyProc.kill();
    pyProc = null;
    pyPort = null;
}

app.on('ready', createPyProc);
app.on('will-quit', exitPyProc);
