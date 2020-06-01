from django.db import migrations


ACTIONS = ['view', 'add', 'change', 'delete']


def replicate_permissions(apps, schema_editor):
    """
    Replicate all Permission assignments as ObjectPermissions.
    """
    Permission = apps.get_model('auth', 'Permission')
    ObjectPermission = apps.get_model('users', 'ObjectPermission')

    # TODO: Optimize this iteration so that ObjectPermissions with identical sets of users and groups
    # are combined into a single ObjectPermission instance.
    for perm in Permission.objects.all():
        # Account for non-standard permission names; e.g. napalm_read
        if perm.codename.split('_')[0] in ACTIONS:
            action = perm.codename.split('_')[0]
        else:
            action = perm.codename

        if perm.group_set.exists() or perm.user_set.exists():
            obj_perm = ObjectPermission(actions=[action])
            obj_perm.save()
            obj_perm.content_types.add(perm.content_type)
            if perm.group_set.exists():
                obj_perm.groups.add(*list(perm.group_set.all()))
            if perm.user_set.exists():
                obj_perm.users.add(*list(perm.user_set.all()))


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_objectpermission'),
    ]

    operations = [
        migrations.RunPython(
            code=replicate_permissions,
            reverse_code=migrations.RunPython.noop
        )
    ]