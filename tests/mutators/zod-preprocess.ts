import { isObject } from '@kyu-asia/core';

export const stripNill = (object: unknown) =>
  isObject(object)
    ? Object.fromEntries(
        Object.entries(object).filter(
          ([_, value]) => value !== null && value !== undefined,
        ),
      )
    : object;
