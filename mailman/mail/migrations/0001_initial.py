# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MailBox'
        db.create_table(u'mail_mailbox', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='boxes', to=orm['auth.User'])),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('enable_dkim', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dkim_key', self.gf('django.db.models.fields.TextField')(null=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'mail', ['MailBox'])

        # Adding model 'Recipient'
        db.create_table(u'mail_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'mail', ['Recipient'])

        # Adding model 'Message'
        db.create_table(u'mail_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mailbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.MailBox'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sender', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('html_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'mail', ['Message'])

        # Adding M2M table for field recipients on 'Message'
        db.create_table(u'mail_message_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('message', models.ForeignKey(orm[u'mail.message'], null=False)),
            ('recipient', models.ForeignKey(orm[u'mail.recipient'], null=False))
        ))
        db.create_unique(u'mail_message_recipients', ['message_id', 'recipient_id'])

        # Adding M2M table for field bcc on 'Message'
        db.create_table(u'mail_message_bcc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('message', models.ForeignKey(orm[u'mail.message'], null=False)),
            ('recipient', models.ForeignKey(orm[u'mail.recipient'], null=False))
        ))
        db.create_unique(u'mail_message_bcc', ['message_id', 'recipient_id'])


    def backwards(self, orm):
        # Deleting model 'MailBox'
        db.delete_table(u'mail_mailbox')

        # Deleting model 'Recipient'
        db.delete_table(u'mail_recipient')

        # Deleting model 'Message'
        db.delete_table(u'mail_message')

        # Removing M2M table for field recipients on 'Message'
        db.delete_table('mail_message_recipients')

        # Removing M2M table for field bcc on 'Message'
        db.delete_table('mail_message_bcc')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mail.mailbox': {
            'Meta': {'object_name': 'MailBox'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'dkim_key': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'enable_dkim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'boxes'", 'to': u"orm['auth.User']"})
        },
        u'mail.message': {
            'Meta': {'object_name': 'Message'},
            'bcc': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mail.Recipient']", 'symmetrical': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'html_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mailbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mail.MailBox']"}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'received_messages'", 'symmetrical': 'False', 'to': u"orm['mail.Recipient']"}),
            'sender': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'mail.recipient': {
            'Meta': {'object_name': 'Recipient'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['mail']