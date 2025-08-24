@echo off
echo Starting reinstallation of VapourSynth packages from GitHub Latest...

:: Create and activate a virtual environment (optional)
:: Uncomment these lines if you want to use a virtual environment
:: python -m venv vs_env
:: call vs_env\Scripts\activate.bat

:: Uninstall existing packages if they exist
echo Removing existing packages...
pip uninstall -y vstransitions vsadjust vspyplugin vspreview lvsfunc vodesfunc jetpytools

:: Install dependencies that might be required
echo Installing dependencies...
pip install -U pip setuptools wheel vsrepo

:: Reinstall the packages directly from GitHub repositories
echo Reinstalling VapourSynth packages from GitHub...

:: lvsfunc
echo Installing lvsfunc...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/lvsfunc

:: vodesfunc
echo Installing vodesfunc...
pip install -U git+https://github.com/Vodes/vodesfunc

:: vstransitions
echo Installing vstransitions...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/vs-transitions

:: vsadjust
echo Installing vsadjust...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/vs-adjust

:: vspyplugin
echo Installing vspyplugin...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/vs-pyplugin

:: muxtools
echo Installing muxtools...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/muxtools

:: vsmuxtools
echo Installing vsmuxtools...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/vs-muxtools

:: vspreview
echo Installing vspreview...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/vs-preview

:: vsjetpack
echo Installing vsjetpack...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/vs-jetpack

:: jetpytools
echo Installing jetpytools...
pip install -U git+https://github.com/Jaded-Encoding-Thaumaturgy/jetpytools

:: vsrepo
echo Installing vsrepo...
vsrepo update && vsrepo upgrade-all

:: Check installation status
echo Verifying installations...
pip list | findstr "vsjetpack muxtools vsmuxtools vspreview lvsfunc vodesfunc vstransitions vsadjust vspyplugin jetpytools"
if %errorlevel% neq 0 (
    echo Some packages failed to install. Please check the output above for errors.
    exit /b 1
)
echo All packages installed successfully!
echo If you are using a virtual environment, remember to deactivate it when done.

echo Reinstallation process completed!

pause