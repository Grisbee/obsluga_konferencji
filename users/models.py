from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
import sys


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.name}'s profile"

    def save(self, *args, **kwargs):
        # Jeśli jest zdjęcie i zostało zmienione, przeskaluj je
        if self.photo and hasattr(self.photo, 'file'):
            try:
                # Otwieramy obraz
                img = Image.open(self.photo)

                # Konwertujemy do RGB jeśli potrzeba (dla formatów jak PNG z przezroczystością)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Ustalamy docelowy rozmiar (150x150 px to przykładowy rozmiar dla kółka)
                output_size = (150, 150)

                # Przycinamy obraz do kwadratu (bierzemy środek)
                width, height = img.size
                if width > height:
                    left = (width - height) / 2
                    top = 0
                    right = width - left
                    bottom = height
                else:
                    top = (height - width) / 2
                    left = 0
                    bottom = height - top
                    right = width

                img = img.crop((left, top, right, bottom))

                # Skalujemy obraz do docelowego rozmiaru
                img = img.resize(output_size, Image.LANCZOS)

                # Zapisujemy przetworzony obraz
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=90)
                output.seek(0)

                # Zastępujemy oryginalne zdjęcie przetworzonym
                self.photo = InMemoryUploadedFile(output, 'ImageField',
                                                  f"{self.photo.name.split('.')[0]}.jpg",
                                                  'image/jpeg',
                                                  sys.getsizeof(output), None)
            except Exception as e:
                print(f"Błąd przetwarzania zdjęcia: {e}")

        super().save(*args, **kwargs)