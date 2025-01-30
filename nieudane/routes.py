def check_all_region_connections(routes_df, regions_df, selected_region):
    def connection_exists(target_region):
        for route in routes_df['route_long_name']:
            if selected_region in route and target_region in route:
                return 1
        return 0

    regions_df['Connection Exists'] = regions_df['Region Name'].apply(connection_exists)
    return regions_df