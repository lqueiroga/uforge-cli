__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from uforge.objects import uforge
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
import pyxb
import datetime
import shlex

class Org_Category_Cmd(Cmd, CoreGlobal):
        """Category operation (list|create|delete|reset)"""

        cmd_name = "category"

        def __init__(self):
                super(Org_Category_Cmd, self).__init__()

        def arg_list(self):
                doParser = ArgumentParser(add_help=True, description="List all the category of the provided organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))

                        org = org_utils.org_get(self.api, doArgs.org)
                        printer.out("Getting category list for ["+org.name+"] . . .")
                        allCategory = self.api.Orgs(org.dbId).Categories.Getall()
                        allCategory = order_list_object_by(allCategory.categories.category, "name")

                        if len(allCategory) is 0:
                                printer.out("["+org.name+"] has no categories.")
                                return 0

                        table = Texttable(200)
                        table.set_cols_align(["l", "l", "l"])
                        table.header(["Id", "Category", "type"])

                        for item in allCategory:
                                table.add_row([item.dbId, item.name, item.type])
                        print table.draw() + "\n"
                        printer.out("Found " + str(len(allCategory)) + " categories.")
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(add_help=True, description="Create one or more categories in the organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the category to create in the organization.")
                mandatory.add_argument('--type', dest='type', type=str, required=True, help="Type of the category to create in the organization. Possible values are : TEMPLATE, PROJECT, IMAGEFORMAT.")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_create(self, args):
                try:
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))

                        org = org_utils.org_get(self.api, doArgs.org)
                        allCategory = self.api.Orgs(org.dbId).Categories.Getall()
                        allCategory = allCategory.categories.category

                        Exist = False
                        for item in allCategory:
                                if doArgs.name == item.name:
                                        Exist = True
                                        printer.out("A category already have the name ["+doArgs.name+"].", printer.ERROR)
                                        return 0

                        if not Exist:
                                newCategory = category()
                                newCategory.name = doArgs.name
                                newCategory.type = doArgs.type

                                result = self.api.Orgs(org.dbId).Categories.Create(body=newCategory)
                                printer.out("Category ["+newCategory.name+"] has successfully been created.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_create()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

        def arg_delete(self):
                doParser = ArgumentParser(add_help=True, description="Delete one or more categories in the organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--name', dest='name', nargs='+', required=False, help="One or more categories to delete (category names provided) in the organization.  Names separated by commas (e.g. cat 1, cat 2, cat 3).")
                optional.add_argument('--ids', dest='ids', nargs='+', required=False, help="One or more categories to delete (category Ids provided) in the organization.  Ids separated by commas (e.g. id1, id2, id3).")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_delete(self, args):
                try:
                        doParser = self.arg_delete()
                        doArgs = doParser.parse_args(shlex.split(args))

                        org = org_utils.org_get(self.api, doArgs.org)
                        allCategory = self.api.Orgs(org.dbId).Categories.Getall()
                        allCategory = allCategory.categories.category

                        deleteList = []
                        if doArgs.name is not None:
                                for arg1 in doArgs.name:
                                        for item in allCategory:
                                                if arg1 == item.name:
                                                        deleteList.append(item)
                                                        break
                        if doArgs.ids is not None:
                                for arg2 in doArgs.ids:
                                        for item2 in allCategory:
                                                if long(arg2) == item2.dbId:
                                                        deleteList.append(item2)
                                                        break

                        for item3 in deleteList:
                                result = self.api.Orgs(org.dbId).Categories.Delete(Id=item3.dbId)
                                printer.out("Category ["+item3.name+"] has been deleted.", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_delete()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()

        def arg_reset(self):
                doParser = ArgumentParser(add_help=True, description="Resets the default categories to the organization")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                return doParser

        def do_reset(self, args):
                try:
                        doParser = self.arg_reset()
                        doArgs = doParser.parse_args(shlex.split(args))

                        org = org_utils.org_get(self.api, doArgs.org)

                        result = self.api.Orgs(org.dbId).Categories.Delete(Reset=True)
                        printer.out("Organization categories has been reseted.", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("In Arguments: "+str(e), printer.ERROR)
                        self.help_reset()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_reset(self):
                doParser = self.arg_reset()
                doParser.print_help()