#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.


import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'

from optparse import make_option

from django.core.management.base import CommandError

from pootle_app.management.commands import PootleCommand
from pootle_app.models import Directory
from pootle_project.models import Project

DUMPED = {
    'TranslationProject': ('pootle_path', 'real_path', 'disabled'),
    'Store': ('file', 'translation_project', 'pootle_path', 'name', 'state'),
    'Directory': ('name', 'parent', 'pootle_path'),
    'Unit': ('source', 'target', 'source_wordcount', 'target_wordcount',
             'developer_comment', 'translator_comment', 'locations',
             'isobsolete', 'isfuzzy', 'istranslated'),
    'Suggestion': ('target_f', 'user_id'),
    'Language': ('code', 'fullname', 'pootle_path'),
    'Project': ('code', 'fullname', 'checkstyle', 'localfiletype',
                'treestyle', 'source_language', 'ignoredfiles',
                'screenshot_search_prefix', 'disabled')
}


class Command(PootleCommand):
    help = "Dump data."

    shared_option_list = (
        make_option('--stats', action='store_true', dest='stats',
                    help='Dump stats'),
        make_option('--data', action='store_true', dest='data',
                    help='Data all data'),
        make_option('--stop-level', action='store', dest='stop_level',
                    default=-1),
        )
    option_list = PootleCommand.option_list + shared_option_list

    def handle_all(self, **options):
        if not self.projects and not self.languages:
            stats = options.get('stats', False)
            data = options.get('data', False)
            stop_level = int(options.get('stop_level', -1))

            if stats:
                self.dump_stats(stop_level=stop_level)
                return
            if data:
                self.dump_all(stop_level=stop_level)
                return

            raise CommandError("Set --data or --stats option.")
        else:
            super(Command, self).handle_all(**options)

    def handle_translation_project(self, tp, **options):
        stats = options.get('stats', False)
        data = options.get('data', False)
        stop_level = int(options.get('stop_level', -1))
        if stats:
            res = {}
            self._dump_stats(tp.directory, res, stop_level=stop_level)
            return

        if data:
            self._dump_item(tp.directory, 0, stop_level=stop_level)
            return

        raise CommandError("Set --data or --stats option.")

    def dump_stats(self, stop_level):
        res = {}
        for prj in Project.objects.all():
            self._dump_stats(prj, res, stop_level=stop_level)

    def _dump_stats(self, item, res, stop_level):
        key = item.get_cachekey()
        item.initialize_children()

        if stop_level != 0 and item.children:
            if stop_level > 0:
                stop_level = stop_level - 1
            for child in item.children:
                self._dump_stats(child, res,
                                 stop_level=stop_level)

        res[key] = (item.get_stats(include_children=False))

        if res[key]['lastaction']:
            last_action_id = res[key]['lastaction']['id']
        else:
            last_action_id = None

        if res[key]['lastupdated']:
            last_updated_id = res[key]['lastupdated']['id']
        else:
            last_updated_id = None

        out = u"%s  %s,%s,%s,%s,%s,%s,%s,%s" % \
              (key, res[key]['total'], res[key]['translated'],
               res[key]['fuzzy'], res[key]['suggestions'],
               res[key]['critical'], res[key]['is_dirty'],
               last_action_id, last_updated_id)

        self.stdout.write(out)

    def dump_all(self, stop_level):
        root = Directory.objects.root
        self._dump_item(root, 0, stop_level=stop_level)

    def _dump_item(self, item, level, stop_level):
        self.stdout.write(self.dumped(item))
        if item.is_dir:
            # item is a Directory
            if item.is_project():
                self.stdout.write(self.dumped(item.project))
            elif item.is_language():
                self.stdout.write(self.dumped(item.language))
            elif item.is_translationproject():
                try:
                    self.stdout.write(self.dumped(item.translationproject))
                except:
                    pass
        else:
            # item should be a Store
            for unit in item.units:
                self.stdout.write(self.dumped(unit))
                for sg in unit.get_suggestions():
                    self.stdout.write(self.dumped(sg))

        if stop_level != level:
            item.initialize_children()
            if item.children:
                for child in item.children:
                    self._dump_item(child, level + 1, stop_level=stop_level)

    def dumped(self, item):
        def get_param(param):
            p = getattr(item, param)
            res = p() if callable(p) else p
            res = u"%s" % res
            res = res.replace('\n', '\\n')
            return (param, res)

        return u"%d:%s\t%s" % \
            (
                item.id,
                item._meta.object_name,
                "\t".join(
                    u"%s=%s" % (k, v)
                    for k, v in map(get_param, DUMPED[item._meta.object_name])
                )
            )
