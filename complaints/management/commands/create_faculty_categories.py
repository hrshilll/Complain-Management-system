from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from complaints.models import UserProfile


class Command(BaseCommand):
    help = "Create one faculty user for each category defined in UserProfile.CATEGORY_CHOICES"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            dest="password",
            default="Passw0rd!",
            help="Default password for created users",
        )
        parser.add_argument(
            "--email-domain",
            dest="email_domain",
            default="example.edu",
            help="Email domain to use for created users",
        )

    def handle(self, *args, **options):
        password = options["password"]
        email_domain = options["email_domain"].lstrip("@")

        faculty_group, _ = Group.objects.get_or_create(name="Faculty")

        created = 0
        skipped = 0

        for value, label in UserProfile.CATEGORY_CHOICES:
            username = f"faculty_{value}"
            email = f"{username}@{email_domain}"

            user, was_created = User.objects.get_or_create(
                username=username, defaults={"email": email}
            )

            if was_created:
                user.set_password(password)
                user.first_name = label.split("/")[0].strip()
                user.last_name = "Faculty"
                user.save()

                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = "faculty"
                profile.category = value
                profile.department = label
                profile.save()

                user.groups.add(faculty_group)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created {username} ({label})"))
            else:
                # Ensure profile is aligned even if user existed
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if profile.role != "faculty" or profile.category != value:
                    profile.role = "faculty"
                    profile.category = value
                    profile.department = label
                    profile.save()
                user.groups.add(faculty_group)
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Exists {username} ({label}) - ensured profile"))

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created: {created}, Updated/Existing: {skipped}")
        )


