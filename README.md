## MIAU BACKEND DJANGO

### Bajar archivo
`git clone <link>`

### Crear entorno virtual para trabajar
#### Windows
1. Ejecutar en terminar `py -m venv neuro-venv`
2. Presionar F1 y escribir `Python: Select Interpreter`
3. Seleccionar el que tiene `neuro-venv`
4. Presionar F1 y escribir `Create New Terminal`
5. Si se instalo correctamente, deberia aparecer a la izquierda `(neuro-venv)`

### Instalacion

1. Ejecutar maquina virtual: Si estas en Windows `.\neuro-venv\Scripts\activate`
2. Instalar requerimientos: `pip install django djangorestframework`

### Comandos importantes

1. Ejecutar servidor `python manage.py runserver`
2. Crear direcorio para trabajar modelos, tests y vistas (Conocidos en django como apps) `python manage.py startapp <nombre>`

### Migrar BD
1. Ejecutar `python manage.py makemigrations`
2. Ejecutar `python manage.py migrate`

#### Nota
Directorios como iser_api fueron creados a mano, creando los 4 archivos mostrados manualmente, por lo que es importante observar como se hicieron.

#### Nota 2 
No borrar ningun archivo del venv o de ni de neurosoft_backend o puede dejar de funcionar la app.

#### Nota 3
No borrar los __init__ pues son necesarios para que funcione cada app creada.

#### Nota 4
No olvidar agregar las apps en el INSTALLED_APPS de wsgi.py en neurosoft_backend para que funcione, ademas de agregar los paths.
