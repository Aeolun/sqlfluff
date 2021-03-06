"""Implementation of Rule L028."""

from ..base import LintResult
from ..doc_decorators import document_configuration
from sqlfluff.core.rules.std.L025 import Rule_L025


@document_configuration
class Rule_L028(Rule_L025):
    """References should be consistent in statements with a single table.

    | **Anti-pattern**
    | In this example, only the field `b` is referenced.

    .. code-block:: sql

        SELECT
            a,
            foo.b
        FROM foo

    | **Best practice**
    |  Remove all the reference or reference all the fields.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo

        -- Also good

        SELECT
            foo.a,
            foo.b
        FROM foo

    """

    config_keywords = ["single_table_references"]

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        """Iterate through references and check consistency."""
        # How many aliases are there? If more than one then abort.
        if len(aliases) > 1:
            return None
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        seen_ref_types = set()
        for ref in references:
            # We skip any unqualified wildcard references (i.e. *). They shouldn't count.
            if not ref.is_qualified() and ref.is_type("wildcard_identifier"):
                continue
            this_ref_type = ref.qualification()
            if self.single_table_references == "consistent":
                if seen_ref_types and this_ref_type not in seen_ref_types:
                    violation_buff.append(
                        LintResult(
                            anchor=ref,
                            description="{0} reference {1!r} found in single table select which is inconsistent with previous references.".format(
                                this_ref_type.capitalize(), ref.raw
                            ),
                        )
                    )
            elif self.single_table_references != this_ref_type:
                violation_buff.append(
                    LintResult(
                        anchor=ref,
                        description="{0} reference {1!r} found in single table select.".format(
                            this_ref_type.capitalize(), ref.raw
                        ),
                    )
                )
            seen_ref_types.add(this_ref_type)

        return violation_buff or None
