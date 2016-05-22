(function () {
    function waitBuildCategoryTree() {
        // Wait for jQuery and the data to be available. This check allows the category tree to work
        // regardless of how the category data is loaded (i.e. JSON or included at render time)
        if ((typeof category_data === "undefined") || (typeof $ === "undefined")) {
            setTimeout(waitBuildCategoryTree, 50);
            return;
        }

        $(function () {
            $("#category_tree").treeview({
                data: category_data,
                levels: 1,
                showTags: true,
                enableLinks: true
            }).on("click", "li", function () {
                // Whenever someone clicks a bottom-level (leaf) category, navigate to the linked page
                var that = $(this);
                if (that.find(".expand-collapse.click-expand, .expand-collapse.click-collapse").size() == 0) {
                    window.location.href = that.find("a[href]").eq(0).attr("href");
                }
            }).on("click", "a", function (event) {
                // When clicking on a link directly, stop event propagation to prevent the category from expanding.
                // Otherwise the category expands as the browser is navigating to a different page
                event.stopPropagation();
            });
        });
    }

    waitBuildCategoryTree();
})();