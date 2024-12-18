from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from web import views as vistas
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Control de acceso
    path('', vistas.RenderHome, name='home'),
    path('login/', vistas.RenderLogin, name='login'),
    path('register/', vistas.RenderRegister, name='register'),
    path('logout/', vistas.Logout, name='logout'),
    
    # Admin
    path('adminHome/', vistas.RenderAdminHome, name='adminHome'),

    path('catalogo/', vistas.RenderCatalogoProductos, name='catalogo'),
    path('productos/', vistas.RenderGestionProductos, name='productos'),
    path('productos/editar/<int:producto_codigo>/', vistas.RenderGestionProductos, name='editarProducto'),
    path('productos/deshabilitar/<str:producto_codigo>/', vistas.DeshabilitarProducto, name='deshabilitarProducto'),

    path('categorias', vistas.RenderGestionCategorias, name='categorias'),
    path('categorias/editar/<int:categoria_id>/', vistas.RenderGestionCategorias, name='editarCategoria'),
    path('categorias/deshabilitar/<int:categoria_id>/', vistas.DeshabilitarCategoria, name='deshabilitarCategoria'),

    path('proveedores/', vistas.RenderGestionProveedores, name='proveedores'),
    path('proveedores/editar/<int:proveedor_id>/', vistas.RenderGestionProveedores, name='editarProveedor'),
    path('proveedores/deshabilitar/<int:proveedor_id>/', vistas.DeshabilitarProveedor, name='deshabilitarProveedor'),

    path('crearPedido/<int:proveedor_id>/', vistas.RenderCrearPedido, name='crearPedido'),
    path('eliminarProductoPedido/<int:codigo_producto>/<int:proveedor_id>/', vistas.EliminarProductoPedido, name='eliminarProductoPedido'),
    path('confirmarPedido/', vistas.ConfirmarPedido, name='confirmarPedido'),

    path('personal/', vistas.RenderPersonal, name='personal'),
    path('personal/edit/<str:rut>/', vistas.EditarPersonal, name='editPersonal'),

    path('reportes/', vistas.RenderReportes, name='reportes'),
    path('reporteVentas/', vistas.ReporteVentas, name='reporteVentas'),
    path('reporteEmpleados/', vistas.ReporteEmpleadoVentas, name='reporteEmpleados'),


    # # Supervisor
    path('superHome', vistas.RenderSuperHome, name='superHome'),
    path('inventario', vistas.RenderInventario, name='inventario'),
    path('ingresoMermas', vistas.RenderIngresoMermas, name='ingresoMermas'),
    path('recepcionPedido', vistas.RenderRecepcionPedido, name='recepcionPedido'),
    path('detallePedido/<int:nro_pedido>/', vistas.RenderDetallePedido, name='detallePedido'),
    path('confirmarRecepcionPedido/<int:nro_pedido>/', vistas.ConfirmarRecepcionPedido, name='confirmarRecepcionPedido'),
    path('cancelarPedido/<int:nro_pedido>/', vistas.CancelarPedido, name='cancelarPedido'),
    path('editarCantidadDetalle/<int:detalle_id>/', vistas.EditarCantidadDetalle, name='editarCantidadDetalle'),
    

    
    # # Vendedor
    path('venta/', vistas.RenderVenta, name='venta'),
    path('confirmarVenta/', vistas.ConfirmarVenta, name='confirmarVenta'),
    path('quitarProductoCarrito/<int:codigo>/', vistas.QuitarProductoCarrito, name='quitarProductoCarrito'),




   #  DOCUMENTACION
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)