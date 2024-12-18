import datetime
from django.contrib import messages

#SESSION
from django.contrib.auth import logout

#HTTP
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from web.forms import CategoriaProducto, CategoriaProductoForm, InventarioForm, LoginForm, ProductoForm, ProveedorForm, RealizarPedido, RegisterForm, VentaForm

#MODEL
from .models import DetallePedido, DetalleVenta, Empleado, Pedido, Producto, Proveedor, Venta

from django.db.models import Q

# ploti
from django.db.models import Count
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from django.db.models import Count
from django.shortcuts import render
from .models import Venta
from django.db.models import Sum
from datetime import datetime


def vendedor_required(view_func):
    """Función decoradora que asegura que el usuario tenga rol de Vendedor."""
    def wrapper(request, *args, **kwargs):
        """Wrapper protector que valida el rol de vendedor antes de permitir el acceso."""
        rol_id = request.session.get('rol_id')
        if rol_id in ["1", "2", "3"]:  
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

def supervisor_required(view_func):
    """Función decoradora que asegura que el usuario tenga rol de Supervisor."""
    def wrapper(request, *args, **kwargs):
        """Wrapper protector que valida el rol de Supervisor antes de permitir el acceso."""
        rol_id = request.session.get('rol_id')
        if rol_id in ["1", "2"]:  # '2' es para Supervisor
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

def admin_required(view_func):
    """Función decoradora que asegura que el usuario tenga rol de Administrador."""
    def wrapper(request, *args, **kwargs):
        """Wrapper protector que valida el rol de administrador antes de permitir el acceso."""
        rol_id = request.session.get('rol_id')
        if rol_id == "1":  # Rol de administrador
            return view_func(request, *args, **kwargs)
        return redirect('login')  # Redirige al login si no es admin
    return wrapper


def Logout(request):
    logout(request)  # Limpia la sesión del usuario
    return redirect('home')

def RenderLogin(request):
    if request.method == 'POST':
        login = LoginForm(request.POST)
        if login.is_valid():
            # cleaned_data es el diccionario que contiene los campos del modelo
            username = login.cleaned_data['username']
            password = login.cleaned_data['password']

            try:
                empleado = Empleado.objects.get(username=username)
                if empleado.check_password(password):
                    request.session['nombre'] = empleado.nombre
                    request.session['rut_empleado'] = empleado.rut_empleado
                    request.session['rol_id'] = str(empleado.rol.id) 
                    print("Rol ID en sesión:", request.session.get('rol_id'))
                    print(f"Rol ID del empleado: {empleado.rol.id}")

                    if empleado.rol.id == 1:
                        return redirect('adminHome')  # Rol de admin
                    elif empleado.rol.id == 2:
                        return redirect('superHome')  # Rol de superusuario
                    elif empleado.rol.id == 3:
                        return redirect('venta')  # Rol de usuario estándar
                    else:
                        return redirect('home')
                else:
                    messages.error(request, 'Credenciales Incorrectas')
                    return render(request, 'shared/login.html', {'form': login})
            except Empleado.DoesNotExist:
                messages.error(request, 'Empleado no existe')
                return render(request, 'shared/login.html', {'form': login})
        else:
            messages.error(request, 'Formulario invalido')
            return render(request, 'shared/login.html', {'form': login})

    elif request.method == 'GET':
        formLogin = LoginForm()
        return render(request, 'shared/login.html', {'form': formLogin})

# @admin_required
def RenderRegister(request):
    if request.method == 'POST':
        register = RegisterForm(request.POST)
        if register.is_valid():
            empleado = register.save(commit=False)  # asigna la variable, pero aun no guarda en db
            empleado.set_password(empleado.password)  # encripta
            empleado.save()                         # guarda
            return redirect('register')
        else:
            # Aquí puedes agregar mensajes de error según el campo específico que esté fallando
            if register.errors.get('rut_empleado'):
                messages.error(request, 'El RUT del empleado ya está registrado.')
            
            if register.errors.get('nombre'):
                messages.error(request, 'El nombre no puede estar vacío.')

            if register.errors.get('apellido'):
                messages.error(request, 'El apellido no puede estar vacío.')

            if register.errors.get('username'):
                messages.error(request, 'El nombre de usuario no puede estar vacío.')

            if register.errors.get('correo'):
                messages.error(request, 'El correo electrónico no es válido o ya está registrado.')

            if register.errors.get('password'):
                messages.error(request, 'La contraseña no puede estar vacía.')

            if register.errors.get('rol'):
                messages.error(request, 'Debe seleccionar un rol válido.')
            return redirect('register')
        
    elif request.method == 'GET':
        form = RegisterForm()
        return render(request, 'admin/personal/register.html', {'form': form})
    
# @admin_required
def EditarPersonal(request, rut):
    try:
        personal = Empleado.objects.get(rut_empleado=rut)
        contraMain = personal.password
    except Empleado.DoesNotExist:
        messages.error(request, 'Usuario no Encontrado')
        return redirect('personal')

    if request.method == 'POST':
        register = RegisterForm(request.POST, instance=personal)
        if register.is_valid():
            empleado = register.save(commit=False)
            passwordFormulario = register.cleaned_data.get('password')
            if passwordFormulario:
                empleado.set_password(passwordFormulario)
            else:
                empleado.password = contraMain
            empleado.save()
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect('personal') 
        else:
            # Aquí puedes agregar mensajes de error según el campo específico que esté fallando
            if register.errors.get('rut_empleado'):
                messages.error(request, 'El RUT del empleado ya está registrado.')
            
            if register.errors.get('nombre'):
                messages.error(request, 'El nombre no puede estar vacío.')

            if register.errors.get('apellido'):
                messages.error(request, 'El apellido no puede estar vacío.')

            if register.errors.get('username'):
                messages.error(request, 'El nombre de usuario no puede estar vacío.')

            if register.errors.get('correo'):
                messages.error(request, 'El correo electrónico no es válido o ya está registrado.')

            if register.errors.get('password'):
                messages.error(request, 'La contraseña no puede estar vacía.')

            if register.errors.get('rol'):
                messages.error(request, 'Debe seleccionar un rol válido.')
            return redirect('editPersonal', rut)
    
    elif request.method == 'GET':
        form = RegisterForm(instance=personal)
        return render(request, 'admin/personal/register.html', {'form': form})

#SHARED
def RenderHome(request):
    """Función que renderiza el home de la página."""
    data = {
        'rut_empleado': request.session.get('rut_empleado'),
        'rol_id': request.session.get('rol_id'),
    }
    return render(request, 'shared/home.html', data)


#ADMINISTRADOR
@admin_required
def RenderAdminHome(request):
    return render(request, 'admin/adminHome.html')

# V.01
# def RenderGestionProductos(request, producto_codigo=None):
#     query = request.GET.get('search', '')  # Obtener el término de búsqueda del input
#     productos = Producto.objects.filter(
#         Q(nombre__icontains=query)  # Buscar por nombre de producto (insensible a mayúsculas/minúsculas)
#     ) if query else Producto.objects.all()  # Si no hay búsqueda, mostrar todos los productos
#     producto = None
#     if producto_codigo:
#         producto = get_object_or_404(Producto, codigo=producto_codigo)
#     if request.method == "POST":
#         form = ProductoForm(request.POST, request.FILES, instance=producto)
#         if form.is_valid():
#             form.save()
#             return redirect("productos")
#     else:
#         form = ProductoForm(instance=producto)
#     context = {
#         'productos': productos,
#         'producto': producto,
#         'query': query,
#         "form": form  # Mantener el término buscado en el input
#     }
#     return render(request, 'admin/gestionTienda/gestionProductos.html', context)

# V.02
@admin_required
def RenderGestionProductos(request, producto_codigo=None):
    query = request.GET.get('search', '')  # Obtener el término de búsqueda del input
    productos = Producto.objects.filter(
        Q(nombre__icontains=query)  # Buscar por nombre de producto (insensible a mayúsculas/minúsculas)
    ) if query else Producto.objects.all()  # Si no hay búsqueda, mostrar todos los productos
    producto = None
    if producto_codigo:
        producto = get_object_or_404(Producto, codigo=producto_codigo)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)  # Asegúrate de incluir request.FILES
        if form.is_valid():
            form.save()
            return redirect("productos")  # Redirige después de guardar el producto
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'productos': productos,
        'producto': producto,
        'query': query,
        "form": form
    }
    return render(request, 'admin/gestionTienda/gestionProductos.html', context)

@admin_required
def DeshabilitarProducto(request, producto_codigo):
    producto = get_object_or_404(Producto, codigo=producto_codigo)
    producto.disponible = not producto.disponible
    producto.save()
    return redirect('productos')  # Redirigir a la lista de productos


@admin_required
def RenderGestionCategorias(request, categoria_id=None):
    query = request.GET.get('search', '') 
    categorias = CategoriaProducto.objects.filter(
        Q(nombre__icontains=query) 
    ) if query else CategoriaProducto.objects.all()

    categoria = None
    if categoria_id:
        categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
    
    if request.method == "POST":
        form = CategoriaProductoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect("categorias")
    else:
        form = CategoriaProductoForm(instance=categoria)
    data = {"form": form, "categorias": categorias, "query": query, "categoria": categoria}
    return render(request, 'admin/gestionTienda/gestionCategorias.html', data)

@admin_required
def DeshabilitarCategoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
    categoria.disponible = not categoria.disponible
    categoria.save()
    return redirect("categorias")

@admin_required
def RenderGestionProveedores(request, proveedor_id=None):
    proveedor = None
    if proveedor_id:
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)

    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect("proveedores")  # Redirigir a la lista tras guardar
    else:
        form = ProveedorForm(instance=proveedor)

    proveedores = Proveedor.objects.all().order_by("nombre")

    return render(request, "admin/proveedores/gestionProveedores.html", {
        "form": form,
        "proveedores": proveedores,
        "proveedor": proveedor 
    })


@admin_required
def DeshabilitarProveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.disponible = not proveedor.disponible
    proveedor.save()
    return redirect('proveedores') 

@admin_required
def RenderCrearPedido(request, proveedor_id):
    query = request.GET.get('search', '')
    productos = Producto.objects.filter(proveedor_id=proveedor_id)
    if query:
        productos = productos.filter(Q(nombre__icontains=query))  # Buscar por nombre de producto
    
    pedido = request.session.get('pedido', [])
    if request.method == "POST":
        codigo_producto = request.POST.get('codigo')
        cantidad = int(request.POST.get('cantidad'))
        try:
            producto = Producto.objects.get(codigo=codigo_producto)
            producto_en_carrito = next((item for item in pedido if str(item['codigo']) == str(codigo_producto)), None)

            if producto_en_carrito:
                producto_en_carrito['cantidad'] += cantidad
                producto_en_carrito['subtotal'] = producto_en_carrito['cantidad'] * producto.precio_compra
            else:
                pedido.append({
                    'codigo': producto.codigo,
                    'nombre': producto.nombre,
                    'precio_unitario': producto.precio_compra,
                    'cantidad': cantidad,
                    'subtotal': cantidad * producto.precio_compra
                })
            request.session['pedido'] = pedido
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')

        return redirect('crearPedido', proveedor_id=proveedor_id)
    
    return render(request, "admin/proveedores/crearPedido.html", {
        'productos': productos,
        'query': query,
        'proveedor_id': proveedor_id,
        'pedido': pedido, 
    })

@admin_required
def EliminarProductoPedido(request, codigo_producto, proveedor_id):
    if request.method == "POST":
        if "pedido" in request.session:
            request.session["pedido"] = [
                item for item in request.session["pedido"] if item["codigo"] != codigo_producto
            ]
            request.session.modified = True 
            messages.success(request, "Producto eliminado del pedido.")
        else:
            messages.error(request, "No se pudo encontrar el pedido en la sesión.")
        return redirect('crearPedido', proveedor_id=proveedor_id)

@admin_required
def ConfirmarPedido(request):
    total_pedido = 0
    proveedor = None 

    for item in request.session["pedido"]:
        producto = Producto.objects.get(codigo=item["codigo"])
        if proveedor is None:
            proveedor = producto.proveedor

    pedido = Pedido.objects.create(
        proveedor=proveedor,
        total_pedido=total_pedido,
    )

    for item in request.session["pedido"]:
        producto = Producto.objects.get(codigo=item["codigo"])
        cantidad = item["cantidad"]
        subtotal = item["subtotal"]
        
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_compra,
            subtotal=subtotal,
        )

        # producto.stock += cantidad
        # producto.save()
        # total_pedido += subtotal  esto fue traspasado a la funcion de supervisor
    pedido.total_pedido = total_pedido
    pedido.save()
    request.session["pedido"] = []
    request.session.modified = True
    return redirect("proveedores")


@admin_required
def RenderPersonal(request, rut=None):
    query = request.GET.get('search', '')
    if query:
        personal = Empleado.objects.filter(Q(nombre__icontains=query))
    else:
        personal = Empleado.objects.all()

    return render(request, 'admin/personal/personal.html', {'empleados': personal, 'search': query})

@admin_required
def RenderReportes(request):
    return render(request, 'admin/reportes/reportes.html')

# Catálogo

# V.01
# def RenderCatalogoProductos(request):
#     query = request.GET.get('search', '')  # Obtener el término de búsqueda
#     productos = Producto.objects.filter(
#         Q(nombre__icontains=query) & Q(disponible=True)  # Buscar productos disponibles por nombre
#     ) if query else Producto.objects.filter(disponible=True)  # Mostrar solo productos disponibles si no hay búsqueda

#     context = {
#         'productos': productos,
#         'query': query
#     }
#     return render(request, 'admin/gestionTienda/verCatalogo.html', context)

# V.02
@supervisor_required
def RenderCatalogoProductos(request):
    query = request.GET.get('search', '')  # Obtener el término de búsqueda
    categoria_id = request.GET.get('categoria', None)  # Capturar el id de la categoría seleccionada
    proveedor_id = request.GET.get('proveedor', None)  # Capturar el id del proveedor seleccionado

    # Filtrar productos por nombre y disponibilidad
    productos = Producto.objects.filter(Q(nombre__icontains=query) & Q(disponible=True)) if query else Producto.objects.filter(disponible=True)

    # Filtrar por categoría si se selecciona una
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtrar por proveedor si se selecciona uno
    if proveedor_id:
        productos = productos.filter(proveedor_id=proveedor_id)

    # Obtener las categorías y proveedores disponibles para los filtros
    categorias = CategoriaProducto.objects.all()
    proveedores = Proveedor.objects.all()

    context = {
        'productos': productos,
        'query': query,
        'categorias': categorias,
        'proveedores': proveedores,
        'categoria_id': categoria_id,
        'proveedor_id': proveedor_id,
    }
    return render(request, 'admin/gestionTienda/verCatalogo.html', context)



#sUPERVISOR
@supervisor_required
def RenderSuperHome(request):
    return render(request, 'supervisor/superHome.html')

@supervisor_required
def RenderInventario(request):
    return render(request, "supervisor/inventario.html")

@supervisor_required
def RenderIngresoMermas(request):
    return render(request, 'supervisor/ingresoMermas.html')

@supervisor_required
def RenderRecepcionPedido(request):
    # Obtener los pedidos confirmados
    pedidos = Pedido.objects.filter(estado="pendiente")  # O usa filtros según tus necesidades
    
    return render(request, "supervisor/recepcionPedido.html", {
        'pedidos': pedidos,
    })

@supervisor_required
def RenderDetallePedido(request, nro_pedido):
    pedido = get_object_or_404(Pedido, nro_pedido=nro_pedido)
    
    # Obtener todos los detalles del pedido
    detalles = pedido.detallePedido.all()  # Aquí 'detallePedido' es el related_name en el modelo DetallePedido

    return render(request, 'supervisor/detallePedido.html', {
        'pedido': pedido,
        'detalles': detalles,
        'proveedor': pedido.proveedor,  # Agregar el proveedor al contexto
    })

@supervisor_required
def ConfirmarRecepcionPedido(request, nro_pedido):
    pedido = get_object_or_404(Pedido, nro_pedido=nro_pedido)
    detalles = pedido.detallePedido.all()
    
    for detalle in detalles:
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()

    pedido.estado = 'confirmado'
    pedido.save()
    
    messages.success(request, f"Pedido #{pedido.nro_pedido}, Proveedor: { producto.proveedor} confirmado. Stock actualizado correctamente.")
    
    return redirect('recepcionPedido')

@supervisor_required
def CancelarPedido(request, nro_pedido):
    pedido = get_object_or_404(Pedido, nro_pedido=nro_pedido)
    pedido.estado = 'cancelado'
    pedido.save()
    return redirect('recepcionPedido')

@supervisor_required
def EditarCantidadDetalle(request, detalle_id):
    detalle = get_object_or_404(DetallePedido, id=detalle_id)
    
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad'))
        detalle.cantidad = nueva_cantidad
        detalle.save()
        
    return redirect('detallePedido', nro_pedido=detalle.pedido.nro_pedido)



#VENDEDOR

# V.01
# def RenderVenta(request):
#     carrito = request.session.get("carrito_venta", [])
#     empleado = request.session.get("nombre", "Empleado no identificado")
#     rol_id = request.session.get("rol_id", "0")  # Aquí obtienes el rol de la sesión como string


#     total_compra = sum(item['subtotal'] for item in carrito)

#     if request.method == "POST":
#         form = VentaForm(request.POST)
#         if form.is_valid():
#             codigo = form.cleaned_data["codigo"]
#             cantidad = form.cleaned_data["cantidad"]

#             # Validación básica de cantidad
#             if cantidad <= 0:
#                 messages.error(request, "La cantidad debe ser mayor que cero.")
#                 return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

#             try:
#                 producto = Producto.objects.get(codigo=codigo)
#             except Producto.DoesNotExist:
#                 messages.error(request, "El producto no existe.")
#                 return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

#             # Validación de stock
#             if producto.stock < cantidad:
#                 messages.error(request, f"Stock insuficiente. Solo quedan {producto.stock} unidades de {producto.nombre}.")
#                 return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

#             subtotal = producto.precio_venta * cantidad

#             # Actualizar o agregar al carrito
#             for item in carrito:
#                 if item["codigo"] == producto.codigo:
#                     item["cantidad"] += cantidad
#                     item["subtotal"] = item["cantidad"] * item["precio_unitario"]
#                     break
#             else:
#                 carrito.append({
#                     "codigo": producto.codigo,
#                     "nombre": producto.nombre,
#                     "precio_unitario": producto.precio_venta,
#                     "cantidad": cantidad,
#                     "subtotal": subtotal,
#                 })

#             # Actualizar el carrito en la sesión
#             request.session["carrito_venta"] = carrito
#             return redirect("venta")

#     else:
#         form = VentaForm()

#     return render(request, "vendedor/venta.html", {
#         "form": form, 
#         "carrito": carrito, 
#         "empleado": empleado,
#         "rol_id": rol_id,
#         "total_compra": total_compra  # Pasamos el total de la compra al template
#     })

# V.02
@vendedor_required
def RenderVenta(request):
    carrito = request.session.get("carrito_venta", [])
    empleado = request.session.get("nombre", "Empleado no identificado")
    rol_id = request.session.get("rol_id", "0")  # Aquí obtienes el rol de la sesión como string

    # Filtrar solo productos habilitados
    productos = Producto.objects.filter(disponible=True)

    total_compra = sum(item['subtotal'] for item in carrito)

    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data["codigo"]
            cantidad = form.cleaned_data["cantidad"]

            # Validación básica de cantidad
            if cantidad <= 0:
                messages.error(request, "La cantidad debe ser mayor que cero.")
                return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

            try:
                producto = Producto.objects.get(codigo=codigo)

                # Verificar si el producto está disponible
                if not producto.disponible:
                    messages.error(request, "El producto está deshabilitado y no puede ser agregado.")
                    return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

            except Producto.DoesNotExist:
                messages.error(request, "El producto no existe.")
                return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

            # Validación de stock
            if producto.stock < cantidad:
                messages.error(request, f"Stock insuficiente. Solo quedan {producto.stock} unidades de {producto.nombre}.")
                return render(request, "vendedor/venta.html", {"form": form, "carrito": carrito, "empleado": empleado, "total_compra": total_compra})

            subtotal = producto.precio_venta * cantidad

            # Actualizar o agregar al carrito
            for item in carrito:
                if item["codigo"] == producto.codigo:
                    item["cantidad"] += cantidad
                    item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                    break
            else:
                carrito.append({
                    "codigo": producto.codigo,
                    "nombre": producto.nombre,
                    "precio_unitario": producto.precio_venta,
                    "cantidad": cantidad,
                    "subtotal": subtotal,
                })

            # Actualizar el carrito en la sesión
            request.session["carrito_venta"] = carrito
            return redirect("venta")

    else:
        form = VentaForm()

    return render(request, "vendedor/venta.html", {
        "form": form, 
        "carrito": carrito, 
        "empleado": empleado,
        "rol_id": rol_id,
        "total_compra": total_compra,  # Pasamos el total de la compra al template
        "productos": productos,  # Pasamos los productos habilitados al template
    })

@vendedor_required
def ConfirmarVenta(request):
    carrito = request.session.get("carrito_venta", [])
    empleado_rut = request.session.get("rut_empleado", "")  # Obtener el RUT del empleado desde la sesión

    if not carrito:
        return redirect("venta")

    try:
        # Obtener la instancia de Empleado utilizando el rut_empleado desde la sesión
        empleado = Empleado.objects.get(rut_empleado=empleado_rut)
        print(f"Empleado encontrado: {empleado}")

        # Crear la instancia de Venta
        venta = Venta.objects.create(
            empleado=empleado,  # Asignamos la instancia de Empleado
            total_venta=0,  # Se calculará posteriormente
        )

        total_venta = 0

        # Crear las instancias de DetalleVenta y actualizar el stock
        for item in carrito:
            producto = Producto.objects.get(codigo=item["codigo"])

            if producto.stock < item["cantidad"]:
                venta.delete()  # Deshacer la venta si hay un error
                return redirect("venta")

            # Crear el detalle de la venta
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                subtotal=item["subtotal"],
            )

            # Actualizar el stock del producto
            producto.stock -= item["cantidad"]
            producto.save()

            # Sumar el subtotal al total de la venta
            total_venta += item["subtotal"]

        # Actualizar el total de la venta
        venta.total_venta = total_venta
        venta.save()

        # Limpiar el carrito
        request.session["carrito_venta"] = []
        return redirect("venta")

    except Empleado.DoesNotExist:
        messages.error(request, f"No se encontró el empleado con RUT {empleado_rut}.")
        return redirect("venta")
    except Exception as e:
        messages.error(request, f"Ocurrió un error al confirmar la compra: {str(e)}")
        return redirect("venta")
    

# @vendedor_required
# def QuitarProductoCarrito(request, codigo):
#     carrito_venta = request.session.get("carrito_venta", [])
#     carrito_venta = [p for p in carrito_venta if p["codigo"] != codigo]
#     request.session["carrito_venta"] = carrito_venta
#     return redirect("venta")


@vendedor_required
def QuitarProductoCarrito(request, codigo):
    carrito_venta = request.session.get("carrito_venta", [])
    new_productos = []
    for producto in carrito_venta:
        if producto["codigo"] != codigo:
            new_productos.append(producto)
    request.session["carrito_venta"] = new_productos
    return redirect("venta")

# Reportes
@admin_required
def ReporteVentas(request):
    # Obtener el mes desde la petición GET (por defecto es noviembre si no se selecciona)
    mes = request.GET.get('mes', datetime.now().month)  # Establecer el mes actual como valor por defecto

    # Filtra las ventas por el mes y año seleccionados
    ventas = Venta.objects.filter(fecha__month=mes, fecha__year=2024)

    # Agrupa las ventas por día
    ventas_por_dia = ventas.values('fecha').annotate(cantidad_ventas=Count('nro_boleta')).order_by('fecha')

    # Datos para el gráfico
    fechas = [v['fecha'] for v in ventas_por_dia]
    cantidad_ventas = [v['cantidad_ventas'] for v in ventas_por_dia]

    # Formatear las fechas para mostrar solo el día
    fechas_formateadas = [fecha.strftime('%d') for fecha in fechas]

    # Calcular el total vendido
    total_vendido = ventas.aggregate(Sum('total_venta'))['total_venta__sum'] or 0

    # Crear el gráfico
    fig, ax = plt.subplots()
    ax.plot(fechas_formateadas, cantidad_ventas, marker='o')

    ax.set(xlabel='Día del mes', ylabel='Cantidad de ventas',
           title='Reporte mensual de ventas')
    ax.grid()

    # Guardar el gráfico como imagen en base64
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Pasar el total vendido al contexto
    return render(request, 'admin/reportes/reporteVentas.html', {
        'image_base64': image_base64,
        'total_vendido': total_vendido,
        'mes': mes  # Pasar el mes seleccionado al contexto para mantenerlo en el formulario
    })

@admin_required
def ReporteEmpleadoVentas(request):
    mes = request.GET.get('mes')

    # Filtra las ventas por el mes seleccionado
    if mes:
        ventas = Venta.objects.filter(fecha__month=mes)
    else:
        # Si no se selecciona un mes, se muestra un mensaje o se filtra por el mes actual
        ventas = Venta.objects.filter(fecha__month=datetime.now().month)

    # Agrupar las ventas por empleado y calcular la cantidad total vendida
    ventas_por_empleado = ventas.values('empleado__nombre').annotate(
        total_vendido=Sum('total_venta'),
        cantidad_ventas=Count('nro_boleta')
    ).order_by('-total_vendido')  # Ordenar de mayor a menor por total vendido

    # Obtener al empleado con más ventas
    top_empleado = ventas_por_empleado.first() if ventas_por_empleado else None

    return render(request, 'admin/reportes/reporteEmpleados.html', {
        'ventas_por_empleado': ventas_por_empleado,
        'top_empleado': top_empleado
    })

