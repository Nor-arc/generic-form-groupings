// Field groups in the browser: the counterpart of field_groups/groups.py's `FieldGroupsMixin`.
// A grouped field's control carries `data-field-group`, `data-field-group-index` and its group's
// conditions as JSON (`data-field-group-when` / `-unless`: field name to values). On every change,
// each group is re-evaluated in index order, as the server does, and its fields are shown or hidden,
// enabled or disabled (a disabled control is not posted, so the server sees what it would have
// cleaned to anyway), and required or not (`data-required-when-active` on the control). A group that
// stops applying also puts its controls back to their defaults, as the server resets a disabled field,
// so switching back later finds nothing stale chosen (a value left from before another choice).
// It knows no field names: `window.nbfg.fieldGroups.bind(form)` wires any form rendered this way.
(function () {
    const CONTROLS = "input, select, textarea";

    // A field's current values, by name within the form; a disabled control holds none.
    const valuesOf = function (form, name) {
        const values = [];
        form.querySelectorAll(`[name="${window.CSS.escape(name)}"]`).forEach(function (el) {
            if (el.disabled) {
                return;
            }
            if (el.type === "radio" || el.type === "checkbox") {
                if (el.checked) {
                    values.push(el.value);
                }
            } else if (el.tagName === "SELECT") {
                Array.from(el.selectedOptions).forEach(function (option) {
                    if (option.value !== "") {
                        values.push(option.value);
                    }
                });
            } else if (el.value !== "") {
                values.push(el.value);
            }
        });
        return values;
    };

    // Back to what the page rendered: an API select emptied, anything else its default value.
    const reset = function (control) {
        if (control.matches("select.nautobot-select2-api")) {
            control.innerHTML = "";
        } else if (control.tagName === "SELECT") {
            Array.from(control.options).forEach(function (option) {
                option.selected = option.defaultSelected;
            });
        } else if (control.type === "checkbox" || control.type === "radio") {
            control.checked = control.defaultChecked;
        } else {
            control.value = control.defaultValue;
        }
        if (control.tagName === "SELECT") {
            // Namespaced, so Select2 redraws without anything reading it as a person's change.
            window.jQuery(control).trigger("change.select2");
        }
    };

    // The element a field is rendered in, label included: the nearest ancestor that also holds the
    // control's `<label for>`. Core's `render_field` puts the label and the control in sibling
    // columns of one row, so the control's own parent is not enough.
    const wrapperOf = function (form, control) {
        const label = control.id ? form.querySelector(`label[for="${window.CSS.escape(control.id)}"]`) : null;
        let wrapper = control.parentElement;
        while (label && wrapper !== form && !wrapper.contains(label)) {
            wrapper = wrapper.parentElement;
        }
        return wrapper;
    };

    const holds = function (form, name, allowed) {
        const wanted = allowed.map(String);
        return valuesOf(form, name).some(function (value) {
            return wanted.includes(value);
        });
    };

    const isActive = function (form, control) {
        const when = JSON.parse(control.dataset.fieldGroupWhen || "{}");
        const unless = JSON.parse(control.dataset.fieldGroupUnless || "{}");
        return (
            Object.entries(when).every(function ([name, allowed]) {
                return holds(form, name, allowed);
            }) &&
            !Object.entries(unless).some(function ([name, excluded]) {
                return holds(form, name, excluded);
            })
        );
    };

    const evaluate = function (form) {
        const groups = new Map();
        form.querySelectorAll("[data-field-group]").forEach(function (control) {
            const wrapper = wrapperOf(form, control);
            const name = control.dataset.fieldGroup;
            if (!groups.has(name)) {
                groups.set(name, { index: Number(control.dataset.fieldGroupIndex), control: control, wrappers: [] });
            }
            if (!groups.get(name).wrappers.includes(wrapper)) {
                groups.get(name).wrappers.push(wrapper);
            }
        });
        // In the server's order, so a field an earlier group just disabled reads as holding nothing.
        Array.from(groups.values())
            .sort(function (a, b) {
                return a.index - b.index;
            })
            .forEach(function (group) {
                const active = isActive(form, group.control);
                group.wrappers.forEach(function (wrapper) {
                    // A wrapper not yet hidden, by the last pass (`d-none`) or by the server's first
                    // paint (`data-field-group-inactive`, which field_groups.css reads), was showing its fields.
                    const wasActive =
                        !wrapper.classList.contains("d-none") && !wrapper.querySelector("[data-field-group-inactive]");
                    wrapper.classList.toggle("d-none", !active);
                    wrapper.querySelectorAll(CONTROLS).forEach(function (control) {
                        control.removeAttribute("data-field-group-inactive");
                        if (wasActive && !active) {
                            reset(control);
                        }
                        control.disabled = !active;
                        if (control.hasAttribute("data-required-when-active")) {
                            control.required = active;
                        }
                    });
                });
            });
        form.dispatchEvent(new CustomEvent("nbfg:field-groups-changed", { bubbles: true }));
    };

    const bind = function (form) {
        // jQuery sees both native changes and Select2's jQuery-only `change`.
        window.jQuery(form).on("change", function () {
            evaluate(form);
        });
        evaluate(form);
    };

    window.nbfg = window.nbfg || {};
    window.nbfg.fieldGroups = { bind: bind };
})();
