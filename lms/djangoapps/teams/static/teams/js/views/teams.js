;(function (define) {
    'use strict';
    define([
        'teams/js/views/team_card',
        'common/js/components/views/paginated_view'
    ], function (TeamCardView, PaginatedView) {
        var TeamsView = PaginatedView.extend({
            type: 'teams',
            cardView: TeamCardView,

            events: {
                'click button.action': '' // entry point for team creation
            },

            render: function () {
                PaginatedView.prototype.render.call(this);

                this.$el.append(
                    $('<button class="action action-primary">' + gettext('Create new team') + '</button>')
                );
                return this;
            }
        });
        return TeamsView;
    });
}).call(this, define || RequireJS.define);