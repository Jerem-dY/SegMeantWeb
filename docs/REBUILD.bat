call .\make.bat clean
cd ..\scripts\python
call pyreverse --output svg --project SegMeant --filter-mode ALL --all-ancestors SegMeant --output-directory uml
call sphinx-apidoc -o ..\..\docs SegMeant --ext-autodoc --ext-imgmath --ext-githubpages --force
cd ..\..
call docs\make.bat html
call .\make.bat clean
