Dim shell, fso, dir
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = dir
shell.Run """C:\Users\hkddr\AppData\Local\Programs\Python\Python311\pythonw.exe"" main.py", 0, False
