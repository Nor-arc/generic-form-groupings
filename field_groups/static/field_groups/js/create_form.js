// Binds field_groups.js and dependent_selects.js to core's create/edit form (`#nb-create-form`),
// on a full page load and for each copy htmx swaps in, and keeps the submit button in step.
// It names no fields.
(function () {
    // Select2 relays all of its events through jQuery only, so native listeners such as an htmx
    // "change from:closest form" trigger never fire. Re-dispatch a real DOM change event.
    const forward = function (event) {
        if (event.originalEvent && event.originalEvent._forwarded) {
            return; // don't loop on our own re-dispatch
        }
        const native = new Event("change", { bubbles: true });
        native._forwarded = true;
        event.target.dispatchEvent(native);
    };

    // Everything that belongs to one rendering of the form.
    const bind = function (form) {
        const submitButton = form.querySelector('button[type="submit"]');

        // The field groups keep `required` in step and disabled controls are never checked, so the
        // browser's constraint check decides.
        const syncSubmitState = function () {
            submitButton.disabled = !form.checkValidity();
        };

        form.querySelectorAll("select").forEach(function (select) {
            window.jQuery(select).on("change", forward);
        });
        window.nbfg.fieldGroups.bind(form);
        window.nbfg.dependentSelects.bind(form);
        // Emptying a select fires Select2's namespaced event only, so these say when to look again.
        form.addEventListener("nbfg:field-groups-changed", syncSubmitState);
        form.addEventListener("nbfg:dependents-cleared", syncSubmitState);
        // Select2 changes bubble here as native events via `forward()` above.
        form.addEventListener("change", syncSubmitState);

        // A re-rendered form comes back with its selections, so it may start ready to submit.
        syncSubmitState();
    };

    // The form's own `hx-on:htmx:load` runs `jsify_form()` (Select2) first: it listens on the form
    // itself, while `htmx.onLoad` listens on the body, which the event reaches later.
    document.addEventListener("DOMContentLoaded", function () {
        window.htmx.onLoad(function (content) {
            const form = content.matches?.("#nb-create-form")
                ? content
                : content.querySelector?.("#nb-create-form");
            if (form) {
                bind(form);
            }
        });
    });
})();
