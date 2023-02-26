call .\make.bat clean
del *.rst
pause
copy CONFIG\index.rst index.rst
pause
cd ..
rem call sphinx-apidoc -o docs .. --ext-autodoc
call sphinx-apidoc -o docs SegMeant --ext-autodoc
pause
rem call sphinx-apidoc -o docs SegMeant/EngineSM/ --ext-autodoc
rem pause
rem call sphinx-apidoc -o docs SegMeant/EngineSM/resources --ext-autodoc -d 6
rem pause
rem call sphinx-apidoc -o docs SegMeant/EngineSM/statistics --ext-autodoc -d 6
rem pause
rem call sphinx-apidoc -o docs SegMeant/EngineSM/tools --ext-autodoc -d 6
rem pause
rem call sphinx-apidoc -o docs SegMeant/EngineSM/tree --ext-autodoc -d 6
rem pause
cd docs
call .\make.bat html

xcopy /s /y html .
