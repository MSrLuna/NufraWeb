from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# UpperCamelCase para las Clases
# snake_case para Metodos
# snake_case para los Atributos de Clases

# Tabla General de Empleados
class Roles(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    disponible = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre 

class Empleado(models.Model):
    rut_empleado = models.CharField(max_length=14, unique=True, primary_key=True,)    
    nombre = models.CharField(max_length=150, default="")
    apellido = models.CharField(max_length=150, default="")
    correo = models.EmailField (max_length=255, unique=True, default="")
    username = models.CharField(max_length=255, unique=True)
    telefono = models.CharField(max_length=16)
    password = models.CharField(max_length=128)  
    rol = models.ForeignKey(Roles, on_delete=models.DO_NOTHING)
    jefatura = models.CharField(max_length=16, null=True, blank=True)
    # cantidad_vendida = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
    
    def set_password(self, raw_password):# contraseñas encriptadas
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password) #crear primer admin por consola, cuardar en txt

    
    # def calcular_cantidad_vendida(self):
    #     return sum(detalle.cantidad * detalle.precio_unitario 
    #                for venta in self.venta.all() 
    #                for detalle in venta.detalle.all())# Suma el total monetario de todas las ventas realizadas por este empleado

    

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, default="")
    correo = models.EmailField(max_length=255) 
    telefono = models.CharField(max_length=16)
    disponible = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre 


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre 

class Producto(models.Model):
    codigo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.DO_NOTHING)
    descripcion = models.TextField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.DO_NOTHING)
    precio_venta = models.FloatField() 
    precio_compra = models.FloatField() 
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='media/producto/', null=True, blank=True)
    stock = models.IntegerField(default=0)


class Inventario(models.Model):
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Inventario {self.id} - {self.categoria.nombre}"
    
class DetalleInventario(models.Model):
    inventario = models.ForeignKey(Inventario, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"


class Venta(models.Model):
    nro_boleta = models.AutoField(unique=True, primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.DO_NOTHING)
    fecha = models.DateField(auto_now_add=True)
    total_venta = models.FloatField()


    def calcular_total(self):
        total = 0  # Inicializamos el total en 0
        for detalle in self.detalleVenta.all():  # Iteramos sobre cada instancia relacionada de DetalleVenta
            subtotal = detalle.cantidad * detalle.precio_unitario  # Calculamos el subtotal para el detalle actual
            total += subtotal  # Sumamos el subtotal al total
        return total  # Devolvemos el total acumulado


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalleVenta")
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()


class Pedido(models.Model):
    estado_choices = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]
    nro_pedido = models.AutoField(unique=True, primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.DO_NOTHING)
    total_pedido = models.FloatField()
    estado = models.CharField(max_length=20, choices=estado_choices, default="pendiente")


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detallePedido")
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()


class Merma(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    total_merma = models.FloatField(default=0.0)  # Para calcular el total de la merma

    def __str__(self):
        return f"Merma #{self.id} - {self.descripcion} - {self.fecha}"

class DetalleMerma(models.Model):
    merma = models.ForeignKey(Merma, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()  # Cantidad de producto perdido o dañado
    razon = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
