from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Izinkan akses hanya untuk pengguna dengan role 'admin'.
    """
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', 'guest') 
        return role == 'admin' 


class IsUserRole(BasePermission):
    """
    Izinkan akses hanya untuk pengguna dengan role 'user'.
    """
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', 'guest')
        return role == 'user'
