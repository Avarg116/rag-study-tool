# 1. build the React app
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN VITE_DEMO_MODE=true npm run build

# 2. serve it with Caddy
FROM caddy:2-alpine
COPY --from=build /app/dist /srv
