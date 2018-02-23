from rest_framework import serializers


class PointSerializer(serializers.Serializer):
    point = serializers.IntegerField()

    def validate_point(self, point):
        if point <= 0:
            raise serializers.ValidationError('point <= 0')
        return point
