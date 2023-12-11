from rest_framework import serializers

from train.models import (
    TrainType,
    Train,
)


class TrainTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True)

    def create(self, validated_data):
        return TrainType.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class TrainSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    cargo_num = serializers.IntegerField(required=True)
    places_in_cargo = serializers.IntegerField(required=True)
    train_type = serializers.PrimaryKeyRelatedField(
        queryset=TrainType.objects.all(), required=False, many=False,
    )
    seats_in_train = serializers.IntegerField(required=False)


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=True)
