from transparance.serializers import ModelSerializer
from transaction.models import Compte

class CompteSerializer(ModelSerializer):
 
    class Meta:
        model = Compte
        fields = ['id', 'name', 'description']