// Dependent API selects: when a field changes, empty every Select2 whose choices were fetched for
// its old value. Core's API selects already declare what they depend on, as query parameters that
// reference another field (`data-query-param-content_type='["$content_type"]'`), so the rule reads
// that markup and needs no field names: `window.nbfg.dependentSelects.bind(form)` wires any form.
(function () {
    const API_SELECT = "select.nautobot-select2-api";

    // Select2 keeps the chosen item as the select's only option, so dropping the options is what
    // clears it. Namespaced so nothing but Select2 reacts, and this rule does not re-trigger itself.
    const clear = function (select) {
        select.innerHTML = "";
        window.jQuery(select).trigger("change.select2");
    };

    // The API selects in `form` whose query parameters reference field `name` ("$name").
    const dependentsOf = function (form, name) {
        const reference = `$${name}`;
        return Array.from(form.querySelectorAll(API_SELECT)).filter(function (select) {
            return Array.from(select.attributes).some(function (attribute) {
                if (!attribute.name.startsWith("data-query-param-")) {
                    return false;
                }
                try {
                    return JSON.parse(attribute.value).includes(reference);
                } catch (error) {
                    return false;
                }
            });
        });
    };

    // Empty everything that depends on `name`, then everything that depends on those, and so on.
    const clearDependentsOf = function (form, name, cleared = new Set()) {
        dependentsOf(form, name).forEach(function (select) {
            if (cleared.has(select.name)) {
                return;
            }
            cleared.add(select.name);
            clear(select);
            clearDependentsOf(form, select.name, cleared);
        });
    };

    const bind = function (form) {
        // `select2:select`/`unselect`/`clear` fire only when a person picks, never for the
        // namespaced event `clear()` sends, so emptying a select does not cascade twice.
        window
            .jQuery(form)
            .on("select2:select select2:unselect select2:clear", "select", function (event) {
                clearDependentsOf(form, event.target.name);
                form.dispatchEvent(new CustomEvent("nbfg:dependents-cleared", { bubbles: true }));
            });
    };

    window.nbfg = window.nbfg || {};
    window.nbfg.dependentSelects = { bind: bind };
})();
